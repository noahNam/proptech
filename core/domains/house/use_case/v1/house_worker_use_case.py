import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from time import time
from typing import List, Optional, Dict

import inject
import requests
from PIL import Image
from sqlalchemy.orm import Query

from app.extensions.utils.image_helper import S3Helper
from app.extensions.utils.log_helper import logger_
from app.extensions.utils.math_helper import MathHelper
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import PublicSaleDetailModel
from core.domains.house.entity.house_entity import (
    AdministrativeDivisionLegalCodeEntity,
    RealEstateLegalCodeEntity,
    PublicSaleEntity,
    UpdateContractStatusTargetEntity,
    RecentlyContractedEntity,
)
from core.domains.house.enum.house_enum import (
    RealTradeTypeEnum,
    PrivateSaleContractStatusEnum,
)
from core.domains.house.repository.house_repository import HouseRepository

logger = logger_.getLogger(__name__)


class BaseHouseWorkerUseCase:
    @inject.autoparams()
    def __init__(self, topic: str, house_repo: HouseRepository):
        self._house_repo = house_repo
        self.topic = topic

    @property
    def client_id(self) -> str:
        return f"{self.topic}-{os.getpid()}"

    def send_slack_message(self, title: str, message: str):
        channel = "#batch-log"

        text = title + "\n" + message
        slack_token = os.environ.get("SLACK_TOKEN")
        if slack_token:
            requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer " + slack_token},
                data={"channel": channel, "text": text},
            )


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

        4. private_sales -> 현재 날짜 기준 3개월 이내 거래 상태 업데이트 (trade_status, deposit_status)
        - private_sales -> 아파트, 오피스텔 건만 업데이트
        - private_sale_details -> max(contract_date): 최근 거래 기준, 매매, 전세만 업데이트
        - 현재 날짜 기준 3개월 이내 거래 건이 있다 -> status: 2
        - 현재 날짜 기준 3개월 이내 거래 건이 없지만 과거 거래가 있다 -> status: 1
        - 거래가 전혀 없다 -> status: 0
    """

    def _calculate_house_acquisition_xax(
        self, private_area: float, supply_price: int
    ) -> int:
        """
            todo: 부동산 정책이 매년 변경되므로 정기적으로 세율 변경 시 업데이트 필요합니다.
            <취득세 계산 2021년도 기준>
            [취득세 계산시, 전용면적을 사용합니다 (공급면적 X)]
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

            acquisition_tax = supply_price * MathHelper.round(
                num=acquisition_tax_rate, decimal_place=2
            )
            local_education_tax = local_education_tax_rate

        elif 60000 < supply_price <= 90000:
            acquisition_tax_rate = (supply_price * 2 / 30000 - 3) * 0.01
            acquisition_tax = supply_price * MathHelper.round(
                num=acquisition_tax_rate, decimal_place=2
            )
            local_education_tax = acquisition_tax * 0.1

        elif 90000 < supply_price:
            acquisition_tax_rate = 0.03
            acquisition_tax = supply_price * MathHelper.round(
                num=acquisition_tax_rate, decimal_place=2
            )
            local_education_tax = local_education_tax_rate

        total_acquisition_tax = MathHelper.round(
            num=acquisition_tax + local_education_tax + rural_special_tax
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

    def _make_private_sale_status_update_list(
        self, target_list: List[UpdateContractStatusTargetEntity]
    ) -> List[dict]:

        result_dict_list = list()

        for target in target_list:
            status = self._get_private_sales_status(
                min_contract_date=target.min_contract_date,
                max_contract_date=target.max_contract_date,
            )
            if target.trade_type == RealTradeTypeEnum.TRADING:
                result_dict_list.append(
                    {
                        "id": target.private_sales_id,
                        "trade_status": status,
                        "updated_at": get_server_timestamp(),
                    }
                )
            elif target.trade_type == RealTradeTypeEnum.LONG_TERM_RENT:
                result_dict_list.append(
                    {
                        "id": target.private_sales_id,
                        "deposit_status": status,
                        "updated_at": get_server_timestamp(),
                    }
                )
            else:
                continue

        return result_dict_list

    def _get_private_sales_status(
        self, min_contract_date: Optional[str], max_contract_date: Optional[str]
    ) -> int:
        today = (datetime.now()).strftime("%Y%m%d")
        three_month_from_today = (datetime.now() - timedelta(days=93)).strftime(
            "%Y%m%d"
        )

        if not min_contract_date or not max_contract_date:
            return PrivateSaleContractStatusEnum.NOTHING.value

        if three_month_from_today <= max_contract_date <= today:
            return PrivateSaleContractStatusEnum.RECENT_CONTRACT.value
        elif max_contract_date <= three_month_from_today:
            return PrivateSaleContractStatusEnum.LONG_AGO.value
        else:
            return PrivateSaleContractStatusEnum.NOTHING.value

    def execute(self):
        logger.info(f"🚀\tPreCalculateAverage Start - {self.client_id}")

        # Batch_step_1 : Upsert_private_sale_avg_prices
        """
            타입이 다르고 평수가 같은 경우가 있는데 이 경우에 평균을 낼 경우 거래일자에 따라 오차가 커질 수 있으므로 둘다 upsert 하고 
            front에서는 최근 거래일 기준에 가까운 것을 보여준다. -> 현재는 같은 평수가 있을 경우 거래일과는 상관없이 랜덤으로 보여주는 중
        """
        try:
            start_time = time()
            logger.info(f"🚀\tUpsert_private_sale_avg_prices : Start")

            create_private_sale_avg_prices_count = 0
            update_private_sale_avg_prices_count = 0
            final_create_list = list()
            final_update_list = list()
            # 매매, 전세 가격 평균 계산
            # target_ids = [idx for idx in range(1, 355105)]
            target_ids = [idx for idx in range(1, 100000)]

            # contract_date 기준 가장 최근에 거래된 row 가져오기
            recent_infos: List[
                RecentlyContractedEntity
            ] = self._house_repo.get_recently_contracted_private_sale_details(
                private_sales_ids=target_ids
            )

            default_pyoung_dict: Dict = self._house_repo.get_default_pyoung_number_for_private_sale(
                target_ids=target_ids
            )

            if recent_infos:
                (
                    avg_price_update_list,
                    avg_price_create_list,
                ) = self._house_repo.make_pre_calc_target_private_sale_avg_prices_list(
                    recent_infos=recent_infos, default_pyoung_dict=default_pyoung_dict,
                )

                final_update_list.extend(avg_price_update_list)
                final_create_list.extend(avg_price_create_list)

            if final_create_list:
                self._house_repo.create_private_sale_avg_prices(
                    create_list=final_create_list
                )
                create_private_sale_avg_prices_count += len(final_create_list)
            else:
                logger.info(
                    f"🚀\tUpsert_private_sale_avg_prices : Nothing avg_price_create_list"
                )

            if final_update_list:
                self._house_repo.update_private_sale_avg_prices(
                    update_list=final_update_list
                )
                update_private_sale_avg_prices_count += len(final_update_list)

            logger.info(
                f"🚀\tUpsert_private_sale_avg_prices : Finished !!, "
                f"records: {time() - start_time} secs, "
                f"{create_private_sale_avg_prices_count} Created, "
                f"{update_private_sale_avg_prices_count} Updated, "
            )

            self.send_slack_message(
                title="🚀 [PreCalculateAverageUseCase Step1] >>> 매매,전세 평균가 계산 배치",
                message=f"Upsert_private_sale_avg_prices : Finished !! \n "
                f"records: {time() - start_time} secs \n "
                f"{create_private_sale_avg_prices_count} Created \n "
                f"{update_private_sale_avg_prices_count} Updated",
            )

        except Exception as e:
            logger.error(f"\tUpsert_private_sale_avg_prices Error - {e}")
            self.send_slack_message(
                title="☠️ [PreCalculateAverageUseCase Step1] >>> 매매,전세 평균가 계산 배치",
                message=f"Upsert_private_sale_avg_prices Error - {e}",
            )
            sys.exit(0)

        # Batch_step_2 : Upsert_public_sale_avg_prices
        # try:
        #     # @Harry -> fail list 에 존재하지 않는 id가 그냥 다 찍히는 것 같습니다. 에러와 구분이 어렵습니다. 수정 부탁드립니다. ex) public_sales_id =  29131, 29132, 29133, 29134 ...
        #     start_time = time()
        #     logger.info(f"🚀\tUpsert_public_sale_avg_prices : Start")
        #
        #     create_public_sale_avg_prices_count = 0
        #     update_public_sale_avg_prices_count = 0
        #     public_sale_avg_prices_failed_list = list()
        #
        #     # 공급 가격 평균 계산
        #     # for idx in range(29130, 42775):
        #     for idx in range(42775, 42785):
        #         competition_and_score_info: dict = self._house_repo.get_competition_and_min_score(
        #             public_sales_id=idx
        #         )
        #         # @Harry count(supply_area)는 의미가 없어서 세대수가 많은 수로 쿼리 바꿨습니다.
        #         default_info: dict = self._house_repo.get_default_infos(
        #             public_sales_id=idx
        #         )
        #
        #         if default_info:
        #             (
        #                 avg_price_update_list,
        #                 avg_price_create_list,
        #             ) = self._house_repo.make_pre_calc_target_public_sale_avg_prices_list(
        #                 public_sales_id=idx,
        #                 default_info=default_info,
        #                 competition_and_score_info=competition_and_score_info,
        #             )
        #             if avg_price_create_list:
        #                 self._house_repo.create_public_sale_avg_prices(
        #                     create_list=avg_price_create_list
        #                 )
        #                 create_public_sale_avg_prices_count += len(
        #                     avg_price_create_list
        #                 )
        #             else:
        #                 logger.info(
        #                     f"🚀\tUpsert_public_sale_avg_prices : Nothing avg_price_create_list"
        #                 )
        #             if avg_price_update_list:
        #                 self._house_repo.update_public_sale_avg_prices(
        #                     update_list=avg_price_update_list
        #                 )
        #                 update_public_sale_avg_prices_count += len(
        #                     avg_price_update_list
        #                 )
        #             else:
        #                 logger.info(
        #                     f"🚀\tUpsert_public_sale_avg_prices : Nothing avg_price_update_list"
        #                 )
        #         else:
        #             public_sale_avg_prices_failed_list.append(idx)
        #
        #     logger.info(
        #         f"🚀\tUpsert_public_sale_avg_prices : Finished !!, "
        #         f"records: {time() - start_time} secs, "
        #         f"{create_public_sale_avg_prices_count} Created, "
        #         f"{update_public_sale_avg_prices_count} Updated, "
        #         f"{len(public_sale_avg_prices_failed_list)} Failed, "
        #         f"Failed_list : {public_sale_avg_prices_failed_list}, "
        #     )
        #
        #     emoji = "🚀"
        #     if public_sale_avg_prices_failed_list:
        #         emoji = "☠️"
        #
        #     self.send_slack_message(
        #         title=f"{emoji} [PreCalculateAverageUseCase Step2] >>> 분양 평균가 계산 배치",
        #         message=f"Upsert_public_sale_avg_prices : Finished !! \n "
        #                 f"records: {time() - start_time} secs \n "
        #                 f"{create_public_sale_avg_prices_count} Created \n "
        #                 f"{update_public_sale_avg_prices_count} Updated \n "
        #                 f"{len(public_sale_avg_prices_failed_list)} Failed \n "
        #                 f"Failed_list : {public_sale_avg_prices_failed_list}"
        #     )
        #
        # except Exception as e:
        #     logger.error(f"🚀\tUpsert_public_sale_avg_prices Error - {e}")
        #     self.send_slack_message(
        #         title="☠️ [PreCalculateAverageUseCase Step2] >>> 분양 평균가 계산 배치",
        #         message=f"Upsert_public_sale_avg_prices Error - {e}"
        #     )
        #     sys.exit(0)

        # Batch_step_3 : Update_public_sale_acquisition_tax
        # try:
        #     start_time = time()
        #     logger.info(f"🚀\tUpdate_public_sale_acquisition_tax : Start")
        #
        #     # PublicSaleDetails.acquisition_tax == 0 건에 대하여 취득세 계산 후 업데이트
        #     target_list = self._house_repo.get_acquisition_tax_calc_target_list()
        #     update_list = list()
        #     if target_list:
        #         update_list = self._make_acquisition_tax_update_list(
        #             target_list=target_list
        #         )
        #     else:
        #         logger.info(
        #             f"🚀\tUpdate_public_sale_acquisition_tax : Nothing acquisition_tax_target_list"
        #         )
        #     if update_list:
        #         self._house_repo.update_acquisition_taxes(update_list=update_list)
        #     else:
        #         logger.info(
        #             f"🚀\tUpdate_public_sale_acquisition_tax : Nothing acquisition_tax_update_list"
        #         )
        #
        #     logger.info(
        #         f"🚀\tUpdate_public_sale_acquisition_tax : Finished !!, "
        #         f"records: {time() - start_time} secs, "
        #         f"{len(update_list)} Updated, "
        #     )
        #     self.send_slack_message(
        #         title=f"🚀 [PreCalculateAverageUseCase Step3] >>> 취득세 계산 배치",
        #         message=f"Update_public_sale_acquisition_tax : Finished !! \n "
        #                 f"records: {time() - start_time} secs \n "
        #                 f"{len(update_list)} Updated"
        #     )
        #
        # except Exception as e:
        #     logger.error(f"🚀\tUpdate_public_sale_acquisition_tax Error - {e}")
        #     self.send_slack_message(
        #         title="☠️ [PreCalculateAverageUseCase Step3] >>> 취득세 계산 배치",
        #         message=f"Update_public_sale_acquisition_tax Error - {e}"
        #     )
        #     sys.exit(0)

        # Batch_step_4 : update_private_sales_status
        # (현재 날짜 기준 최근 3달 거래 여부 업데이트)
        # @Harry 현재날짜 기준이 아니라 마지막 최종 거래일인 것 같습니다. step1과 어떤점이 다른지 잘모르겠습니다. 이부분 하실때 저한테 확인 먼저 부탁드립니다.
        # try:
        #     start_time = time()
        #     logger.info(f"🚀\tUpdate_private_sales_status : Start")
        #
        #     target_ids = self._house_repo.get_private_sales_all_id_list()
        #
        #     target_list: List[
        #         UpdateContractStatusTargetEntity
        #     ] = self._house_repo.get_update_status_target_of_private_sale_details(
        #         private_sales_ids=target_ids
        #     )
        #
        #     update_list = self._make_private_sale_status_update_list(
        #         target_list=target_list
        #     )
        #
        #     self._house_repo.bulk_update_status_to_private_sales(
        #         update_list=update_list
        #     )
        #
        #     logger.info(
        #         f"🚀\tUpdate_private_sales_status : Finished !!, "
        #         f"records: {time() - start_time} secs, "
        #         f"{len(update_list)} Updated, "
        #     )
        #
        #     self.send_slack_message(
        #         title=f"🚀 [PreCalculateAverageUseCase Step4] >>> 현재 날짜 기준 최근 3달 거래 여부 업데이트",
        #         message=f"Update_private_sales_status : Finished !! \n "
        #                 f"records: {time() - start_time} secs \n "
        #                 f"{len(update_list)} Updated"
        #     )
        #
        # except Exception as e:
        #     logger.error(f"🚀\tUpdate_private_sales_status Error - {e}")
        #     self.send_slack_message(
        #         title="☠️ [PreCalculateAverageUseCase Step4] >>> 현재 날짜 기준 최근 3달 거래 여부 업데이트",
        #         message=f"Update_private_sales_status Error - {e}"
        #     )
        #     sys.exit(0)
        #
        # sys.exit(0)


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

            emoji = "🚀"
            if failure_list:
                emoji = "☠️"

            self.send_slack_message(
                title=f"{emoji} [PreCalculateAdministrativeDivisionUseCase] >>> 행정구역별 매매,전세 평균가 계산",
                message=f"PreCalculateAdministrativeDivisionUseCase : Finished !! \n "
                f"records: {time() - start_time} secs \n "
                f"{len(update_list)} Updated"
                f"{len(failure_list)} Failed"
                f"Failed_list : {failure_list}",
            )

        except Exception as e:
            logger.error(f"🚀\tPreCalculateAdministrative Error - {e}")
            self.send_slack_message(
                title="☠️ [PreCalculateAverageUseCase Step4] >>> 현재 날짜 기준 최근 3달 거래 여부 업데이트",
                message=f"PreCalculateAdministrative Error - {e}",
            )
            sys.exit(0)

        exit(os.EX_OK)


class AddLegalCodeUseCase(BaseHouseWorkerUseCase):
    def _make_real_estates_legal_code_update_list(
        self,
        administrative_info: List[AdministrativeDivisionLegalCodeEntity],
        target_list: List[RealEstateLegalCodeEntity],
    ) -> List[dict]:
        """
            real_estates.jibun_address 주소가 없을 경우 혹은 건축예정이라 불확실한 경우 직접 매뉴얼 작업 필요
            todo: '동탄X동' 주소가 올 경우 하위 구성하는 동에 대한 별도 로직 필요
        """
        update_list = list()
        failed_list = list()
        cond_1 = re.compile(r"\D*동\d가")
        cond_2 = re.compile(r"\D*\d동")

        for real_estate in target_list:
            for administrative in administrative_info:
                # 예) 용산동2가 -> 행정구역에 용산동이랑 매칭되는지 확인
                if cond_1.match(real_estate.dong_myun):
                    dong_myun_ = re.sub(r"[0-9]+가", "", real_estate.dong_myun)
                    if administrative.short_name != dong_myun_:
                        dong_myun_ = real_estate.dong_myun
                else:
                    dong_myun_ = real_estate.dong_myun

                # 예) 안양1동 -> 안양동으로 처리하여 행정구역 안양동과 매칭되는지 확인
                if cond_2.match(real_estate.jibun_address) and not cond_2.match(
                    administrative.short_name
                ):
                    jibun_address_ = re.sub(r"[0-9]+", "", real_estate.jibun_address)
                    dong_myun_ = re.sub(r"[0-9]+", "", dong_myun_)
                else:
                    jibun_address_ = real_estate.jibun_address

                # 예외) 충주 목행동 + 용탄동 -> 목행.용탄동 통합
                if real_estate.dong_myun == "목행동" or real_estate.dong_myun == "용탄동":
                    dong_myun_ = "목행.용탄동"
                    if real_estate.dong_myun == "목행동":
                        jibun_address_ = jibun_address_.replace("목행동", dong_myun_)
                    elif real_estate.dong_myun == "용탄동":
                        jibun_address_ = jibun_address_.replace("용탄동", dong_myun_)

                administrative_name_ = administrative.name.replace(" ", "").replace(
                    ".", ""
                )
                administrative_short_name_ = administrative.short_name.replace(".", "")
                jibun_address_ = jibun_address_.replace(" ", "").replace(".", "")

                si_do_ = real_estate.si_do.replace(" ", "")
                si_gun_gu_ = real_estate.si_gun_gu.replace(" ", "")
                dong_myun_ = dong_myun_.replace(".", "")

                if (
                    administrative_short_name_ == dong_myun_
                    and si_do_ in administrative_name_
                    and si_gun_gu_ in administrative_name_
                    and administrative_name_ in jibun_address_
                ):
                    front_legal_code = administrative.front_legal_code
                    back_legal_code = administrative.back_legal_code

                    update_dict = {
                        "id": real_estate.id,
                        "front_legal_code": front_legal_code,
                        "back_legal_code": back_legal_code,
                    }
                    update_list.append(update_dict)
                    print(f"updated list : id - {real_estate.id}")
                    break
            failed_list.append(real_estate.id)
        return update_list

    def execute(self):
        start_time = time()
        logger.info(f"🚀\tAddLegalCodeUseCase Start - {self.client_id}")

        administrative_info = (
            self._house_repo.get_administrative_divisions_legal_code_info_all_list()
        )
        real_estate_info = self._house_repo.get_real_estates_legal_code_info_all_list()

        if not administrative_info:
            logger.info(
                f"🚀\tAddLegalCodeUseCase : administrative_divisions_legal_code_info_list"
            )
            exit(os.EX_OK)
        if not real_estate_info:
            logger.info(f"🚀\tAddLegalCodeUseCase : real_estates_legal_code_info_list")
            exit(os.EX_OK)
        update_list = self._make_real_estates_legal_code_update_list(
            administrative_info=administrative_info, target_list=real_estate_info
        )

        try:
            self._house_repo.update_legal_code_to_real_estates(update_list=update_list)
        except Exception as e:
            logger.error(
                f"🚀\tAddLegalCodeUseCase - update_legal_code_to_real_estates "
                f"error : {e}"
            )
        logger.info(
            f"🚀\tAddLegalCodeUseCase : Finished !!, "
            f"records: {time() - start_time} secs, "
            f"{len(update_list)} Updated, "
        )

        exit(os.EX_OK)


class InsertUploadPhotoUseCase(BaseHouseWorkerUseCase):
    """
        <아래 테이블의 이미지를 업로드 합니다.>
        - public_sale_photos
        - public_sale_detail_photos

        <사용 방법>
        업로드 할 폴더들(예: e편한세상 강일 어반브릿지(42384))을 app/extensions/utils/upload_images_list/에 넣고 worker 실행
        업로드 후 app/upload_images_list 내 업로드 폴더들 삭제해야 합니다. (tanos 용량 증가, 동일 이미지 다시 업로드 방지)
        upload_images_list 디렉토리는 커밋에 올리지 않습니다. 사용 후 제거 해주세요.

        <Manual 실행 시 주의 사항>
        config.py AWS 관련 config 시크릿 값 직접 넣어주어야 합니다
        S3Helper().upload() 함수 -> bucket 이름 직접 넣어주어야 합니다.
        테스트시 DB sequence 경우에 따라 초기화해줘야 할 필요가 있습니다. (전부 삭제 후 다시 업로드시)
        업로드 대상 폴더 내에 중복 public_sale_details_id가 없어야 합니다 - 사전에 제거 필요(예: 윗층-아랫층)
        업로드 대상 폴더 내에 평면도 없음(폴더) 가 없어야 합니다 - 사전에 제거 필요
        파일명: 이름(PK) -> PK가 없는 파일 이름은 업로드 무시하고 넘어갑니다

        todo: 빈 폴더 Exception (통과되도록), 지나간 폴더 목록 logger, update 로직(가능하면 s3 삭제(나중))
    """

    def collect_file_list(self, dir_list, file_list, dir_idx) -> dict:
        """
            파일 확장자 정규화 처리
            '.JPG' or '.jpg' -> '.jpeg'
            '.PNG' -> '.png'
        """
        entry = list()
        result_dict = dict()
        for image_name in file_list:
            path = S3Helper().get_image_upload_dir() + "/" + dir_list[dir_idx] + "/"
            full_path = Path(
                S3Helper().get_image_upload_dir()
                + "/"
                + dir_list[dir_idx]
                + "/"
                + image_name
            )
            if os.path.splitext(image_name)[-1] in [".JPG", ".jpg"]:
                changed_image_name = os.path.splitext(image_name)[0] + ".jpeg"
                before_img = Image.open(full_path)
                before_img.save(fp=Path(path + changed_image_name), format="jpeg")
                os.rename(src=full_path, dst=Path(path + changed_image_name))

            elif os.path.splitext(image_name)[-1] in [".PNG"]:
                changed_image_name = os.path.splitext(image_name)[0] + ".png"
                before_img = Image.open(full_path)
                before_img.save(fp=Path(path + changed_image_name), format="png")
            entry.append(image_name)

        result_dict[dir_list[dir_idx]] = entry
        return result_dict

    def make_upload_list(
        self, dir_name: list, file_list, photos_start_idx, detail_photos_start_idx
    ):
        logger.info(f"🚀\tUpload_target : {dir_name[0]}")

        public_sale_photos_start_idx = photos_start_idx
        public_sale_detail_photos_start_idx = detail_photos_start_idx
        public_sale_photos = list()
        public_sale_detail_photos = list()

        for image_list in file_list:
            for image_name in image_list:
                if "@" in image_name:
                    # @ 문자가 있는 파일 이름 : public_sale_photos 테이블 upload 대상
                    table_name = "public_sale_photos"
                    is_thumbnail = False

                    public_sales_id = int(dir_name[0].split("(")[1].rsplit(")")[0])

                    if self._house_repo.is_enable_public_sale_house(
                        house_id=public_sales_id
                    ):

                        seq = int(image_name.split("@")[0]) - 1
                        if seq == 0:
                            is_thumbnail = True
                        file_name = image_name.split("@")[1].split(".")[0]
                        extension = (
                            os.path.splitext(image_name)[-1].split(".")[1].lower()
                        )
                        path = S3Helper().get_image_upload_uuid_path(
                            image_table_name=table_name, extension=extension
                        )

                        public_sale_photos.append(
                            {
                                "id": public_sale_photos_start_idx,
                                "public_sales_id": public_sales_id,
                                "file_name": file_name,
                                "path": path,
                                "extension": extension,
                                "is_thumbnail": is_thumbnail,
                                "seq": seq,
                                "created_at": get_server_timestamp(),
                            }
                        )
                        file_name = (
                            S3Helper().get_image_upload_dir()
                            + r"/"
                            + dir_name[0]
                            + r"/"
                            + image_name
                        )

                        S3Helper().upload(
                            bucket="toadhome-tanos-bucket",
                            file_name=file_name,
                            object_name=path,
                            extension=extension,
                        )
                        public_sale_photos_start_idx = public_sale_photos_start_idx + 1
                    else:
                        logger.info(f"🚀\tpublic_sales_id : {public_sales_id} failed")
                else:
                    table_name = "public_sale_detail_photos"
                    try:
                        public_sale_details_id = int(
                            image_name.split("(")[1].rsplit(")")[0]
                        )

                        if self._house_repo.is_enable_public_sale_detail_info(
                            public_sale_details_id
                        ):

                            file_name = image_name.split("(")[0]
                            extension = (
                                os.path.splitext(image_name)[-1].split(".")[1].lower()
                            )
                            path = S3Helper().get_image_upload_uuid_path(
                                image_table_name=table_name, extension=extension
                            )
                            public_sale_detail_photos.append(
                                {
                                    "id": public_sale_detail_photos_start_idx,
                                    "public_sale_details_id": public_sale_details_id,
                                    "file_name": file_name,
                                    "path": path,
                                    "extension": extension,
                                    "created_at": get_server_timestamp(),
                                }
                            )

                            file_name = (
                                S3Helper().get_image_upload_dir()
                                + r"/"
                                + dir_name[0]
                                + r"/"
                                + image_name
                            )
                            S3Helper().upload(
                                bucket="toadhome-tanos-bucket",
                                file_name=file_name,
                                object_name=path,
                                extension=extension,
                            )
                            public_sale_detail_photos_start_idx = (
                                public_sale_detail_photos_start_idx + 1
                            )
                        else:
                            logger.info(
                                f"🚀\tpublic_sales_detail_id : {public_sale_details_id} failed"
                            )

                    except Exception:
                        # FK 없는 이미지 이름은 제외
                        continue

            return public_sale_photos, public_sale_detail_photos

    def execute(self):
        logger.info(f"🚀\tInsertUploadPhotoUseCase Start - {self.client_id}")
        logger.info(f"🚀\tupload_job 위치 : {S3Helper().get_image_upload_dir()}")
        start_time = time()

        _dirs = None
        cnt = 0

        recent_public_sale_photos_info = (
            self._house_repo.get_recent_public_sale_photos()
        )
        recent_public_sale_detail_photos_info = (
            self._house_repo.get_recent_public_sale_detail_photos()
        )

        if not recent_public_sale_photos_info:
            public_sale_photos_start_idx = 1
        else:
            public_sale_photos_start_idx = recent_public_sale_photos_info.id

        if not recent_public_sale_detail_photos_info:
            public_sale_detail_photos_start_idx = 1
        else:
            public_sale_detail_photos_start_idx = (
                recent_public_sale_detail_photos_info.id
            )

        upload_list: List[Dict] = list()
        for (roots, dirs, file_names) in os.walk(S3Helper().get_image_upload_dir()):
            entry = []
            if len(dirs) > 0:
                _dirs = dirs
            if len(file_names) > 0:
                for file_name in file_names:
                    entry.append(file_name)

                upload_list.append(
                    self.collect_file_list(dir_list=_dirs, file_list=entry, dir_idx=cnt)
                )
                cnt = cnt + 1

        for entry in upload_list:
            key = list(entry.keys())
            values = list(entry.values())

            (public_sale_photos, public_sale_detail_photos) = self.make_upload_list(
                dir_name=key,
                file_list=values,
                photos_start_idx=public_sale_photos_start_idx,
                detail_photos_start_idx=public_sale_detail_photos_start_idx,
            )
            # Bulk insert public_sale_photos
            try:
                self._house_repo.insert_images_to_public_sale_photos(
                    create_list=public_sale_photos
                )
                logger.info(
                    f"🚀\t [insert_images_to_public_sale_photos] - Done! "
                    f"{len(public_sale_photos)} finished, "
                    f"records: {time() - start_time} secs"
                )
            except Exception as e:
                logger.error(f"insert_images_to_public_sale_photos error : {e}")
                exit(os.EX_OK)

            # Bulk insert public_sale_detail_photos
            try:
                self._house_repo.insert_images_to_public_sale_detail_photos(
                    create_list=public_sale_detail_photos
                )
                logger.info(
                    f"🚀\t [insert_images_to_public_sale_detail_photos] - Done! "
                    f"{len(public_sale_detail_photos)} created, "
                    f"records: {time() - start_time} secs"
                )
            except Exception as e:
                logger.error(f"insert_images_to_public_sale_photos error : {e}")
                exit(os.EX_OK)

            public_sale_photos_start_idx = public_sale_photos_start_idx + len(
                public_sale_photos
            )
            public_sale_detail_photos_start_idx = (
                public_sale_detail_photos_start_idx + len(public_sale_detail_photos)
            )

        exit(os.EX_OK)
