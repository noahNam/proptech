import os
import sys
from datetime import datetime, timedelta
from time import time
from typing import List, Dict

import inject
import requests
import sentry_sdk
from sqlalchemy.orm import Query

from app.extensions.utils.log_helper import logger_
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import PublicSaleDetailModel
from core.domains.house.repository.house_repository import HouseRepository

logger = logger_.getLogger(__name__)


class BaseHouseWorkerUseCase:
    @inject.autoparams()
    def __init__(self, topic: str, house_repo: HouseRepository):
        self._house_repo = house_repo
        self.topic = topic

    def send_slack_message(self, message: str):
        channel = "#engineering-class"

        text = "[Batch Error] PreCalculateAverageUseCase -> " + message
        slack_token = os.environ.get("SLACK_TOKEN")
        requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer " + slack_token},
            data={"channel": channel, "text": text},
        )

    @property
    def client_id(self) -> str:
        return f"{self.topic}-{os.getpid()}"


class PreCalculateAverageUseCase(BaseHouseWorkerUseCase):
    """
        <목적 : 해당되는 매물을 가져와 필요한 평균값, 계산값을 미리 계산하여 저장한다>
        1. 모든 real_estates row 대상으로
        - private_sale_id 1개 해당되는 private_sale_details 평균 계산 -> private_sale_avg_prices
        - (가장 최근에 updated된 row를 가져온다 -> contract_date 기준 1달 이전 범위 필터링)
        - (하나의 아파트 실거래에 평수가 여러가지 있으므로, 같은 평수끼리 모아 평균 계산하여 Insert-> private_sale_avg_prices)
        - public_sale_id 1개 해당되는 public_sale_details 타입별 분양가 평균 계산 -> public_sale_avg_prices

        2. Default pyoung 값 선정
        - 지도에 나타낼 대표 평수를 구한다 -> 공급면적(supply_area) 값 -> 평수 변환
        - private_sale_details.group_by(private_sales_id).count() -> 제일 많은 카운트 선정
        - 새로운 아파트가 없으면 -> 가장 낮은 평수를 Default pyoung 선정

        3. public_sale_details -> 취득세 계산
        - 매물 상세 페이지 -> 최대 최소 취득세의 경우 SQL max, min func() 쿼리 사용
    """

    def _calculate_house_acquisition_xax(
        self, private_area: float, supply_price: int
    ) -> int:
        """
            todo: 부동산 정책이 매년 변경되므로 정기적으로 세율 변경 시 업데이트 필요합니다.
            <취득세 계산 2021년도 기준>
            (부동산 종류가 주택일 경우로 한정합니다 - 상가, 오피스텔, 토지, 건물 제외)
            [parameters]
            - private_area: 전용면적
                if 85 < private_area -> 85(제곱미터) 초과 시 농어촌특별세 0.2% 과세 계산 추가
                    -> rural_special_tax = supply_price * 0.2%
            - supply_price: 공급금액 (DB 저장 단위: 만원)

            - acquisition_tax_rate : 취득세 적용세율
                if supply_price <= 60000: -> [6억원 이하] -> 1.0%
                elif 60000 < supply_price <= 90000: -> [6억 초과 ~ 9억 이하]
                    -> acquisition_tax_rate = (supply_price * 2 / 30000 - 3) * 1.0%
                elif 90000 < supply_price: -> [9억 초과] -> 3.0%

            - local_education_tax_rate : 지방 교육세율
                if supply_price < 60000: -> [6억원 이하] -> 0.1%
                elif 60000 < supply_price <= 90000: -> [6억 초과 ~ 9억 이하]
                    -> local_education_tax_rate = acquisition_tax * 0.1 (취득세의 1/10)
                elif 90000 < supply_price: -> [9억 초과] -> 0.3%

            [return]
            - total_acquisition_tax : 최종 취득세
                - acquisition_tax(취득세 본세) + local_education_tax(지방교육세) + rural_special_tax(농어촌특별세)
        """
        if (
            not private_area
            or private_area == 0
            or not supply_price
            or supply_price == 0
        ):
            return 0

        rural_special_tax, rural_special_tax_rate = 0, 0.0
        acquisition_tax, acquisition_tax_rate = 0, 0.0
        local_education_tax, local_education_tax_rate = 0, 0.0

        if 85 < private_area:
            rural_special_tax_rate = 0.2
            rural_special_tax = supply_price * rural_special_tax_rate * 0.01

        if supply_price <= 60000:
            acquisition_tax_rate = 0.01
            local_education_tax_rate = 0.01

            acquisition_tax = supply_price * round(acquisition_tax_rate, 2)
            local_education_tax = local_education_tax_rate

        elif 60000 < supply_price <= 90000:
            acquisition_tax_rate = (supply_price * 2 / 30000 - 3) * 0.01
            acquisition_tax = supply_price * round(acquisition_tax_rate, 2)
            local_education_tax = acquisition_tax * 0.1

        elif 90000 < supply_price:
            acquisition_tax_rate = 0.03
            acquisition_tax = supply_price * round(acquisition_tax_rate, 2)
            local_education_tax = local_education_tax_rate

        total_acquisition_tax = round(
            acquisition_tax + local_education_tax + rural_special_tax
        )

        return total_acquisition_tax

    def _make_acquisition_tax_update_list(
        self, target_list: List[PublicSaleDetailModel]
    ) -> List[dict]:
        result_dict_list = list()
        for target in target_list:
            result_dict_list.append(
                {
                    "id": target.id,
                    "acquisition_tax": self._calculate_house_acquisition_xax(
                        private_area=target.private_area,
                        supply_price=target.supply_price,
                    ),
                    "updated_at": get_server_timestamp(),
                }
            )
        return result_dict_list

    def execute(self):
        logger.info(f"🚀\tPreCalculateAverage Start - {self.client_id}")

        # # Batch_step_1 : Upsert_private_sale_avg_prices
        # try:
        #     start_time = time()
        #     logger.info(f"🚀\tUpsert_private_sale_avg_prices : Start")
        #
        #     create_private_sale_avg_prices_count = 0
        #     update_private_sale_avg_prices_count = 0
        #     final_create_list = list()
        #     final_update_list = list()
        #     private_sale_avg_prices_failed_list = list()
        #     # 매매, 전세 가격 평균 계산
        #     target_ids = [idx for idx in range(650001, 1000001)]
        #     # target_ids = [1, 2]
        #
        #     # contract_date 기준 가장 최근에 거래된 row 가져오기
        #     recent_infos: List[
        #         RecentlyContractedEntity
        #     ] = self._house_repo.get_recently_contracted_private_sale_details(
        #         private_sales_ids=target_ids
        #     )
        #
        #     default_pyoung_dict: Dict = self._house_repo.get_default_pyoung_number_for_private_sale(
        #         target_ids=target_ids
        #     )
        #
        #     if recent_infos:
        #         # avg_prices_info : [(supply_area, avg_trade_prices, avg_deposit_prices), ...]
        #         (
        #             avg_price_update_list,
        #             avg_price_create_list,
        #         ) = self._house_repo.make_pre_calc_target_private_sale_avg_prices_list(
        #             recent_infos=recent_infos, default_pyoung_dict=default_pyoung_dict,
        #         )
        #
        #         final_update_list.extend(avg_price_update_list)
        #         final_create_list.extend(avg_price_create_list)
        #
        #     if final_create_list:
        #         self._house_repo.create_private_sale_avg_prices(
        #             create_list=final_create_list
        #         )
        #         create_private_sale_avg_prices_count += len(final_create_list)
        #     else:
        #         logger.info(
        #             f"🚀\tUpsert_private_sale_avg_prices : Nothing avg_price_create_list"
        #         )
        #
        #     if final_update_list:
        #         self._house_repo.update_private_sale_avg_prices(
        #             update_list=final_update_list
        #         )
        #         update_private_sale_avg_prices_count += len(final_update_list)
        #
        #     # private_sale_avg_prices_failed_list.append(recent_info.private_sales_id)
        #     logger.info(
        #         f"🚀\tUpsert_private_sale_avg_prices : Finished !!, "
        #         f"records: {time() - start_time} secs, "
        #         f"{create_private_sale_avg_prices_count} Created, "
        #         f"{update_private_sale_avg_prices_count} Updated, "
        #         # f"{len(private_sale_avg_prices_failed_list)} Failed, "
        #         # f"Failed_list : {private_sale_avg_prices_failed_list}, "
        #     )
        #     # step 1까지만 실행
        #     sys.exit(0)
        #
        # except Exception as e:
        #     logger.error(f"🚀\tUpsert_private_sale_avg_prices Error - {e}")
        #     self.send_slack_message(
        #         message=f"🚀\tUpsert_private_sale_avg_prices Error - {e}"
        #     )
        #     sys.exit(0)
        #
        # # Batch_step_2 : Upsert_public_sale_avg_prices
        # try:
        #     start_time = time()
        #     logger.info(f"🚀\tUpsert_public_sale_avg_prices : Start")
        #
        #     create_public_sale_avg_prices_count = 0
        #     update_public_sale_avg_prices_count = 0
        #     public_sale_avg_prices_failed_list = list()
        #
        #     # 공급 가격 평균 계산
        #     for idx in range(29130, 42437):
        #         avg_supply_price_info = self._house_repo.get_pre_calc_avg_prices_target_of_public_sales(
        #             public_sales_id=idx
        #         )
        #         default_pyoung = self._house_repo.get_default_pyoung_number_for_public_sale(
        #             public_sales_id=idx
        #         )
        #         # avg_supply_price_info : [(supply_area, avg_trade_prices), ...]
        #         if avg_supply_price_info:
        #             (
        #                 avg_price_update_list,
        #                 avg_price_create_list,
        #             ) = self._house_repo.make_pre_calc_target_public_sale_avg_prices_list(
        #                 public_sales_id=idx,
        #                 query_set=avg_supply_price_info,
        #                 default_pyoung=default_pyoung,
        #             )
        #             if avg_price_create_list:
        #                 try:
        #                     self._house_repo.create_public_sale_avg_prices(
        #                         create_list=avg_price_create_list
        #                     )
        #                     create_public_sale_avg_prices_count += len(
        #                         avg_price_create_list
        #                     )
        #                 except Exception as e:
        #                     logger.error(
        #                         f"Upsert_public_sale_avg_prices - create_public_sale_avg_prices "
        #                         f"public_sales_id : {idx} error : {e}"
        #                     )
        #             else:
        #                 logger.info(
        #                     f"🚀\tUpsert_public_sale_avg_prices : Nothing avg_price_create_list"
        #                 )
        #             if avg_price_update_list:
        #                 try:
        #                     self._house_repo.update_public_sale_avg_prices(
        #                         update_list=avg_price_update_list
        #                     )
        #                     update_public_sale_avg_prices_count += len(
        #                         avg_price_update_list
        #                     )
        #                 except Exception as e:
        #                     logger.error(
        #                         f"Upsert_public_sale_avg_prices - update_public_sale_avg_prices "
        #                         f"public_sales_id : {idx} error : {e}"
        #                     )
        #             else:
        #                 logger.info(
        #                     f"🚀\tUpsert_public_sale_avg_prices : Nothing avg_price_update_list"
        #                 )
        #         else:
        #             public_sale_avg_prices_failed_list.append(idx)
        #     logger.info(
        #         f"🚀\tUpsert_public_sale_avg_prices : Finished !!, "
        #         f"records: {time() - start_time} secs, "
        #         f"{create_public_sale_avg_prices_count} Created, "
        #         f"{update_public_sale_avg_prices_count} Updated, "
        #         f"{len(public_sale_avg_prices_failed_list)} Failed, "
        #         f"Failed_list : {public_sale_avg_prices_failed_list}, "
        #     )
        # except Exception as e:
        #     logger.error(f"🚀\tUpsert_public_sale_avg_prices Error - {e}")
        #     self.send_slack_message(
        #         message=f"🚀\tUpsert_public_sale_avg_prices Error - {e}"
        #     )
        #     sentry_sdk.capture_exception(e)
        #     sys.exit(0)

        # Batch_step_3 : Update_public_sale_acquisition_tax
        # try:
        #     start_time = time()
        #     logger.info(f"🚀\tUpdate_public_sale_acquisition_tax : Start")
        #
        #     # PublicSaleDetails.acquisition_tax == 0 건에 대하여 취득세 계산 후 업데이트
        #     target_list = self._house_repo.get_acquisition_tax_calc_target_list()
        #     update_list = None
        #     if target_list:
        #         update_list = self._make_acquisition_tax_update_list(
        #             target_list=target_list
        #         )
        #     else:
        #         logger.info(
        #             f"🚀\tUpdate_public_sale_acquisition_tax : Nothing acquisition_tax_target_list"
        #         )
        #     if update_list:
        #         try:
        #             self._house_repo.update_acquisition_taxes(update_list=update_list)
        #         except Exception as e:
        #             logger.error(
        #                 f"Update_public_sale_acquisition_tax - update_acquisition_taxes "
        #                 f"error : {e}"
        #             )
        #     else:
        #         logger.info(
        #             f"🚀\tUpdate_public_sale_acquisition_tax : Nothing acquisition_tax_update_list"
        #         )
        #     logger.info(
        #         f"🚀\tUpdate_public_sale_acquisition_tax : Finished !!, "
        #         f"records: {time() - start_time} secs, "
        #         f"{len(update_list)} Updated, "
        #     )
        # except Exception as e:
        #     logger.error(f"🚀\tUpdate_public_sale_acquisition_tax Error - {e}")
        #     self.send_slack_message(
        #         message=f"🚀\tUpdate_public_sale_acquisition_tax Error - {e}"
        #     )
        #     sentry_sdk.capture_exception(e)
        #     sys.exit(0)
        #
        # exit(os.EX_OK)


class PreCalculateAdministrativeDivisionUseCase(BaseHouseWorkerUseCase):
    """
        Administrative_divisions 평균 계산
        - level 별 name 값
        - 예시) level_1 : 서울특별시, level_2: 서울특별시 종로구, level_3: 서울특별시 종로구 인사동
        - real_estates.jibun_address -> 해당 name이 속하는 모든 row List를 가져온다
        - private_sales -> rent_type -> 전세 / 월세 / 매매 별로 private_sale_details의 해당 평균을 구한다.
        - public_sales -> 분양가 평균(public_sale_price)을 구한다.
        - 예시) 서울특별시 -> 서울특별시에 해당되는 모든 매물
    """

    def execute(self):
        logger.info(f"🚀\tPreCalculateAdministrative Start - {self.client_id}")
        try:
            """
                1. real_estates 를 행정구역코드로 묶는다.
                2. 1번의 결과에서 평균가를 구한다.
                    -> 평균가 구입 시 단순 avg가 아니라 34평 기준 평균을 구한다.
                3. 평균가를 Administrative_divisions에 밀어 넣는다.
            """
            start_time = time()

            # si_do
            two_month_from_today = int(
                (datetime.now() - timedelta(days=60)).strftime("%Y%m")
            )
            common_query_object: Query = self._house_repo.get_common_query_object(
                yyyymm=two_month_from_today
            )
            lv1_list: List[dict] = self._house_repo.get_si_do_avg_price(
                sub_q=common_query_object
            )
            lv2_list: List[dict] = self._house_repo.get_si_gun_gu_avg_price(
                sub_q=common_query_object
            )
            lv3_list: List[dict] = self._house_repo.get_dong_myun_avg_price(
                sub_q=common_query_object
            )

            result_list = lv1_list + lv2_list + lv3_list

            # 2191 / 2190
            # administrative_division_id를 bind하고 맵핑 되지 않는 리스트를 반환한다.
            update_list, failure_list = self._house_repo.set_administrative_division_id(
                result_list=result_list
            )

            self._house_repo.update_avg_price_to_administrative_division(
                update_list=update_list
            )

            logger.info(
                f"🚀\tPreCalculateAdministrativeDivisionUseCase : Finished !!, "
                f"records: {time() - start_time} secs, "
                f"{len(result_list)} Updated, "
                f"{len(failure_list)} Failed, "
                f"Failed_list : {failure_list}, "
            )

        except Exception as e:
            logger.error(f"🚀\tPreCalculateAdministrative Error - {e}")
            self.send_slack_message(
                message=f"🚀\tPreCalculateAdministrative Error - {e}"
            )
            sentry_sdk.capture_exception(e)
            sys.exit(0)

        exit(os.EX_OK)
