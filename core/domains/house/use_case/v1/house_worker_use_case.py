import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from time import time, sleep
from typing import List, Optional, Dict

import inject
import requests
import xmltodict
from PIL import Image
from sqlalchemy.orm import Query

from app.extensions.utils.house_helper import HouseHelper
from app.extensions.utils.image_helper import ImageHelper, ImageNameCollector, S3Helper
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
    CheckIdsRealEstateEntity,
    AddSupplyAreaEntity,
    BindTargetSupplyAreaEntity,
    BindFailureSupplyAreaEntity,
    BindSuccessSupplyAreaEntity,
)
from core.domains.house.enum.house_enum import (
    RealTradeTypeEnum,
    PrivateSaleContractStatusEnum,
    ReplacePublicToPrivateSalesEnum,
    BuildTypeEnum,
    HouseBatchTimeDelta,
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
        text = title + "\n" + message
        slack_token = os.environ.get("SLACK_TOKEN")
        slack_channel = os.environ.get("SLACK_CHANNEL")
        if slack_token:
            requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer " + slack_token},
                data={"channel": slack_channel, "text": text},
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
        - private_sale_details.group_by(private_sale_id).count() -> 제일 많은 카운트 선정
        - 새로운 아파트가 없으면 -> 가장 낮은 평수를 Default pyoung 선정

        3. public_sale_details -> 취득세 계산
        - 매물 상세 페이지 -> 최대 최소 취득세의 경우 SQL max, min func() 쿼리 사용

        4. private_sales -> 현재 날짜 기준 N 개월 이내 거래 상태 업데이트 (trade_status, deposit_status)
        - N 개월 설정 : HouseBatchTimeDelta Enum
        - private_sales -> 아파트, 오피스텔 건만 업데이트
        - private_sale_details -> max(contract_date): 최근 거래 기준, 매매, 전세만 업데이트
        - 현재 날짜 기준 N개월 이내 거래 건이 있다 -> status: 2
        - 현재 날짜 기준 N개월 이내 거래 건이 없지만 과거 거래가 있다 -> status: 1
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
                        "id": target.private_sale_id,
                        "trade_status": status,
                        "updated_at": get_server_timestamp(),
                    }
                )
            elif target.trade_type == RealTradeTypeEnum.LONG_TERM_RENT:
                result_dict_list.append(
                    {
                        "id": target.private_sale_id,
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
        timedelta_from_today = (
            datetime.now() - timedelta(days=HouseBatchTimeDelta.SIX_MONTH.value)
        ).strftime("%Y%m%d")

        if not min_contract_date or not max_contract_date:
            return PrivateSaleContractStatusEnum.NOTHING.value

        if timedelta_from_today <= max_contract_date <= today:
            return PrivateSaleContractStatusEnum.RECENT_CONTRACT.value
        elif max_contract_date <= timedelta_from_today:
            return PrivateSaleContractStatusEnum.LONG_AGO.value
        else:
            return PrivateSaleContractStatusEnum.NOTHING.value

    def execute(self):
        logger.info(f"🚀\tPreCalculateAverage Start - {self.client_id}")

        # Batch_step_1 : Upsert_public_sale_avg_prices
        public_batch_flag = True
        try:
            start_time = time()
            logger.info(f"🚀\tUpsert_public_sale_avg_prices : Start")

            create_public_sale_avg_prices_count = 0
            update_public_sale_avg_prices_count = 0
            public_sale_avg_prices_failed_list = list()

            # 공급 가격 평균 계산
            target_ids = (
                self._house_repo.get_target_list_of_upsert_public_sale_avg_prices()
            )
            if not target_ids:
                logger.info(
                    f"🚀\tUpsert_public_sale_avg_prices : Nothing target_ids for batch, passed step_1"
                )

            else:
                for idx in target_ids:
                    competition_and_score_info: dict = self._house_repo.get_competition_and_min_score(
                        public_sale_id=idx
                    )
                    default_info: dict = self._house_repo.get_default_infos(
                        public_sale_id=idx
                    )

                    if default_info:
                        (
                            avg_price_update_list,
                            avg_price_create_list,
                        ) = self._house_repo.make_pre_calc_target_public_sale_avg_prices_list(
                            public_sale_id=idx,
                            default_info=default_info,
                            competition_and_score_info=competition_and_score_info,
                        )
                        if avg_price_create_list:
                            self._house_repo.create_public_sale_avg_prices(
                                create_list=avg_price_create_list
                            )
                            create_public_sale_avg_prices_count += len(
                                avg_price_create_list
                            )
                        else:
                            logger.info(
                                f"🚀\tUpsert_public_sale_avg_prices : Nothing avg_price_create_list"
                            )
                        if avg_price_update_list:
                            self._house_repo.update_public_sale_avg_prices(
                                update_list=avg_price_update_list
                            )
                            update_public_sale_avg_prices_count += len(
                                avg_price_update_list
                            )
                        else:
                            logger.info(
                                f"🚀\tUpsert_public_sale_avg_prices : Nothing avg_price_update_list"
                            )
                    else:
                        public_sale_avg_prices_failed_list.append(idx)

            logger.info(
                f"🚀\tUpsert_public_sale_avg_prices : Finished !!, "
                f"records: {time() - start_time} secs, "
                f"{create_public_sale_avg_prices_count} Created, "
                f"{update_public_sale_avg_prices_count} Updated, "
                f"{len(public_sale_avg_prices_failed_list)} Failed, "
                f"Failed_list : {public_sale_avg_prices_failed_list}, "
            )

            emoji = "🚀"
            if public_sale_avg_prices_failed_list:
                emoji = "☠️"

            self.send_slack_message(
                title=f"{emoji} [PreCalculateAverageUseCase Step1] >>> 분양 평균가 계산 배치",
                message=f"Upsert_public_sale_avg_prices : Finished !! \n "
                f"records: {time() - start_time} secs \n "
                f"{create_public_sale_avg_prices_count} Created \n "
                f"{update_public_sale_avg_prices_count} Updated \n "
                f"{len(public_sale_avg_prices_failed_list)} Failed \n "
                f"Failed_list : {public_sale_avg_prices_failed_list}",
            )

        except Exception as e:
            logger.error(f"🚀\tUpsert_public_sale_avg_prices Error - {e}")
            self.send_slack_message(
                title="☠️ [PreCalculateAverageUseCase Step1] >>> 분양 평균가 계산 배치",
                message=f"Upsert_public_sale_avg_prices Error - {e}",
            )
            public_batch_flag = False

        # Batch_step_2 : Update_public_sale_acquisition_tax
        if public_batch_flag:
            try:
                start_time = time()
                logger.info(f"🚀\tUpdate_public_sale_acquisition_tax : Start")

                # PublicSaleDetails.acquisition_tax == 0 건에 대하여 취득세 계산 후 업데이트
                target_list: List[
                    PublicSaleDetailModel
                ] = self._house_repo.get_acquisition_tax_calc_target_list()
                update_list = list()
                if not target_list:
                    logger.info(
                        f"🚀\tUpdate_public_sale_acquisition_tax : Nothing acquisition_tax_target_list"
                    )
                else:
                    update_list = self._make_acquisition_tax_update_list(
                        target_list=target_list
                    )
                    if update_list:
                        self._house_repo.update_acquisition_taxes(
                            update_list=update_list
                        )
                    else:
                        logger.info(
                            f"🚀\tUpdate_public_sale_acquisition_tax : Nothing acquisition_tax_update_list"
                        )

                self.send_slack_message(
                    title=f"🚀 [PreCalculateAverageUseCase Step2] >>> 취득세 계산 배치",
                    message=f"Update_public_sale_acquisition_tax : Finished !! \n "
                    f"records: {time() - start_time} secs \n "
                    f"{len(update_list)} Updated",
                )

            except Exception as e:
                logger.error(f"🚀\tUpdate_public_sale_acquisition_tax Error - {e}")
                self.send_slack_message(
                    title="☠️ [PreCalculateAverageUseCase Step2] >>> 취득세 계산 배치",
                    message=f"Update_public_sale_acquisition_tax Error - {e}",
                )
        else:
            logger.info(
                f"🚀\tUpdate_public_sale_acquisition_tax : passed step_2 due to step_1 failed"
            )

        # Batch_step_3 : Upsert_private_sale_avg_prices
        """
            타입이 다르고 평수가 같은 경우가 있는데 이 경우에 평균을 낼 경우 거래일자에 따라 오차가 커질 수 있으므로 둘다 upsert 하고
            front에서는 최근 거래일 기준에 가까운 것을 보여준다. -> 현재는 같은 평수가 있을 경우 거래일과는 상관없이 랜덤으로 보여주는 중
        """
        private_batch_flag = True
        try:
            start_time = time()
            logger.info(f"🚀\tUpsert_private_sale_avg_prices : Start")

            create_private_sale_avg_prices_count = 0
            update_private_sale_avg_prices_count = 0
            final_create_list = list()
            final_update_list = list()

            # 매매, 전세 가격 평균 계산
            # target_ids = [idx for idx in range(1, 355105)]
            target_ids = self._house_repo.get_target_of_upsert_private_sale_avg_prices()

            if not target_ids:
                logger.info(f"🚀\tUpsert_private_sale_avg_prices : Nothing target_ids")

            else:
                # contract_date 기준 가장 최근에 거래된 row 가져오기
                recent_infos: List[
                    RecentlyContractedEntity
                ] = self._house_repo.get_recently_contracted_private_sale_details(
                    private_sale_ids=target_ids
                )

                default_pyoung_dict: Dict = self._house_repo.get_default_pyoung_number_for_private_sale(
                    target_ids=target_ids
                )

                if recent_infos:
                    (
                        avg_price_update_list,
                        avg_price_create_list,
                    ) = self._house_repo.make_pre_calc_target_private_sale_avg_prices_list(
                        recent_infos=recent_infos,
                        default_pyoung_dict=default_pyoung_dict,
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
                title="🚀 [PreCalculateAverageUseCase Step3] >>> 매매,전세 평균가 계산 배치",
                message=f"Upsert_private_sale_avg_prices : Finished !! \n "
                f"records: {time() - start_time} secs \n "
                f"{create_private_sale_avg_prices_count} Created \n "
                f"{update_private_sale_avg_prices_count} Updated",
            )

        except Exception as e:
            logger.error(f"\tUpsert_private_sale_avg_prices Error - {e}")
            self.send_slack_message(
                title="☠️ [PreCalculateAverageUseCase Step3] >>> 매매,전세 평균가 계산 배치",
                message=f"Upsert_private_sale_avg_prices Error - {e}",
            )
            private_batch_flag = False

        # Batch_step_4 : update_private_sales_status
        # (현재 날짜 기준 최근 N개월 거래 여부 업데이트)
        if private_batch_flag:
            update_list = list()
            try:
                start_time = time()
                logger.info(f"🚀\tUpdate_private_sales_status : Start")

                target_ids = self._house_repo.get_private_sales_all_id_list()
                if not target_ids:
                    logger.info(f"🚀\tUpdate_private_sales_status : Nothing target_ids")

                else:
                    target_list: List[
                        UpdateContractStatusTargetEntity
                    ] = self._house_repo.get_update_status_target_of_private_sale_details(
                        private_sale_ids=target_ids
                    )

                    update_list = self._make_private_sale_status_update_list(
                        target_list=target_list
                    )

                    self._house_repo.bulk_update_private_sales(update_list=update_list)

                    logger.info(
                        f"🚀\tUpdate_private_sales_status : Finished !!, "
                        f"records: {time() - start_time} secs, "
                        f"{len(update_list)} Updated, "
                    )

                self.send_slack_message(
                    title=f"🚀 [PreCalculateAverageUseCase Step4] >>> 현재 날짜 기준 최근 6달 거래 여부 업데이트",
                    message=f"Update_private_sales_status : Finished !! \n "
                    f"records: {time() - start_time} secs \n "
                    f"{len(update_list)} Updated",
                )

            except Exception as e:
                logger.error(f"🚀\tUpdate_private_sales_status Error - {e}")
                self.send_slack_message(
                    title="☠️ [PreCalculateAverageUseCase Step4] >>> 현재 날짜 기준 최근 6달 거래 여부 업데이트",
                    message=f"Update_private_sales_status Error - {e}",
                )
        else:
            logger.info(
                f"🚀\tUpdate_private_sales_status : passed step_4 due to step_3 failed"
            )

        sys.exit(0)


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
                (
                    datetime.now() - timedelta(days=HouseBatchTimeDelta.SIX_MONTH.value)
                ).strftime("%Y%m")
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
                title="☠️ [PreCalculateAdministrativeDivisionUseCase] >>> 행정구역별 매매,전세 평균가 계산",
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
        real_estate_info = (
            self._house_repo.get_real_estates_legal_code_info_should_update_list()
        )

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
            self.send_slack_message(
                title="☠️ [AddLegalCodeUseCase] >>> New real_estates - 법정코드 부여 배치",
                message=f"update_legal_code_to_real_estates Error - {e}",
            )
        failure_list = (
            self._house_repo.get_real_estates_legal_code_info_should_update_list()
        )

        logger.info(
            f"🚀\tAddLegalCodeUseCase : Finished !!, "
            f"records: {time() - start_time} secs, "
            f"{len(update_list) if update_list else 0} Updated, "
            f"{len(failure_list) if failure_list else 0} Failed"
        )

        emoji = "🚀"

        if failure_list:
            emoji = "☠️"

        self.send_slack_message(
            title=f"{emoji} [AddLegalCodeUseCase] >>> New real_estates - 법정코드 부여 배치",
            message=f"AddLegalCodeUseCase : Finished !! \n "
            f"records: {time() - start_time} secs \n "
            f"{len(update_list) if update_list else 0} Updated, "
            f"{len(failure_list) if failure_list else 0} Failed"
            f"Failed_list : {failure_list}",
        )

        exit(os.EX_OK)


class UpsertUploadPhotoUseCase(BaseHouseWorkerUseCase):
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
        업로드 대상 폴더 내에 중복 public_sale_detail_id가 없어야 합니다 - 사전에 제거 필요(예: 윗층-아랫층)
        업로드 대상 폴더 내에 평면도 없음(폴더) 가 없어야 합니다 - 사전에 제거 필요
        파일명: 이름(PK) -> PK가 없는 파일 이름은 업로드 무시하고 넘어갑니다

        todo: update 로직(가능하면 s3 삭제(나중))
    """

    def collect_file_list(self, dir_name: str, file_list: List[str]) -> Optional[dict]:
        """
            파일 확장자 정규화 처리
            '.JPG' or '.jpg' -> '.jpeg'
            '.PNG' -> '.png'
        """
        entry = list()
        result_dict = dict()
        failed_list = list()

        for image_name in file_list:
            changed_image_name = None
            path = ImageHelper().get_image_upload_dir() + "/" + dir_name + "/"
            full_path = Path(
                ImageHelper().get_image_upload_dir() + "/" + dir_name + "/" + image_name
            )
            if os.path.splitext(image_name)[-1] in [".JPG", ".jpg"]:
                changed_image_name = os.path.splitext(image_name)[0] + ".jpeg"
                before_img = Image.open(full_path)
                convert_img = before_img.convert("RGB")
                try:
                    convert_img.save(fp=Path(path + changed_image_name), format="jpeg")
                    os.rename(src=full_path, dst=Path(path + changed_image_name))
                except Exception as e:
                    print(f"Error - {e}, {dir_name}, {image_name}")
                    failed_list.append(f"{dir_name} - {image_name}")
                    continue

            elif os.path.splitext(image_name)[-1] in [".PNG"]:
                changed_image_name = os.path.splitext(image_name)[0] + ".png"
                before_img = Image.open(full_path)
                before_img.save(fp=Path(path + changed_image_name), format="png")
            if changed_image_name:
                entry.append(changed_image_name)
            else:
                entry.append(image_name)

        if failed_list:
            print(f"{failed_list}")
        result_dict[dir_name] = entry
        return result_dict

    def make_upload_list(
        self, dir_name: str, file_list, photos_start_idx, detail_photos_start_idx
    ):
        logger.info(f"🚀\tUpload_target : {dir_name}")

        public_sale_photos_start_idx = photos_start_idx
        public_sale_detail_photos_start_idx = detail_photos_start_idx
        public_sale_photos = list()
        public_sale_detail_photos = list()

        failed_public_sale_ids = list()
        failed_public_sale_detail_ids = list()
        failed_public_sale_image_names = list()
        failed_public_sale_detail_image_names = list()
        passed_image_names_dict = dict()

        # 폴더 내 이미지 파일들 목록 Loop
        for image_list in file_list:
            # 이미지 파일별 파일 이름 체크 Loop
            for image_name in image_list:
                if "@" in image_name:
                    # @ 문자가 있는 파일 이름 : public_sale_photos 테이블 upload 대상
                    table_name = "public_sale_photos"
                    is_thumbnail = False

                    public_sale_id = int(dir_name.split("(")[1].rsplit(")")[0])

                    if self._house_repo.is_enable_public_sale_house(
                        house_id=public_sale_id
                    ):

                        seq = int(image_name.split("@")[0]) - 1
                        if seq == 0:
                            is_thumbnail = True
                        file_name = image_name.split("@")[1].split(".")[0]
                        extension = (
                            os.path.splitext(image_name)[-1].split(".")[1].lower()
                        )
                        path = S3Helper().get_image_upload_uuid_path(
                            image_table_name=table_name,
                            dir_name=dir_name,
                            extension=extension,
                        )

                        public_sale_photos.append(
                            {
                                "id": public_sale_photos_start_idx,
                                "public_sale_id": public_sale_id,
                                "file_name": file_name,
                                "path": path,
                                "extension": extension,
                                "is_thumbnail": is_thumbnail,
                                "seq": seq,
                                "created_at": get_server_timestamp(),
                                "updated_at": get_server_timestamp(),
                            }
                        )
                        file_name = (
                            ImageHelper().get_image_upload_dir()
                            + r"/"
                            + dir_name
                            + r"/"
                            + image_name
                        )
                        # S3 upload
                        S3Helper().upload(
                            bucket="toadhome-tanos-bucket",
                            dir_name=dir_name,
                            file_name=file_name,
                            object_name=path,
                            extension=extension,
                        )
                        public_sale_photos_start_idx = public_sale_photos_start_idx + 1
                    else:
                        # public_sale_photos 실패 수집
                        failed_public_sale_ids.append(public_sale_id)
                        failed_public_sale_image_names.append(image_name)
                else:
                    # public_sale_detail_photos 테이블 upload 대상
                    table_name = "public_sale_detail_photos"
                    try:
                        public_sale_detail_id = int(
                            image_name.split("(")[1].rsplit(")")[0]
                        )

                        if self._house_repo.is_enable_public_sale_detail_info(
                            public_sale_detail_id
                        ):

                            file_name = image_name.split("(")[0]
                            extension = (
                                os.path.splitext(image_name)[-1].split(".")[1].lower()
                            )
                            path = S3Helper().get_image_upload_uuid_path(
                                image_table_name=table_name,
                                dir_name=dir_name,
                                extension=extension,
                            )
                            public_sale_detail_photos.append(
                                {
                                    "id": public_sale_detail_photos_start_idx,
                                    "public_sale_detail_id": public_sale_detail_id,
                                    "file_name": file_name,
                                    "path": path,
                                    "extension": extension,
                                    "created_at": get_server_timestamp(),
                                    "updated_at": get_server_timestamp(),
                                }
                            )

                            file_name = (
                                ImageHelper().get_image_upload_dir()
                                + r"/"
                                + dir_name
                                + r"/"
                                + image_name
                            )
                            # S3 upload
                            S3Helper().upload(
                                bucket="toadhome-tanos-bucket",
                                file_name=file_name,
                                dir_name=dir_name,
                                object_name=path,
                                extension=extension,
                            )
                            public_sale_detail_photos_start_idx = (
                                public_sale_detail_photos_start_idx + 1
                            )
                        else:
                            # public_sale_details_photos 실패 수집
                            failed_public_sale_detail_ids.append(public_sale_detail_id)
                            failed_public_sale_detail_image_names.append(image_name)
                    except Exception:
                        # FK 없는 이미지 이름은 제외
                        passed_image_names_dict[dir_name] = image_name
                        continue

        # 실패 리스트 로그 기록
        if failed_public_sale_ids and failed_public_sale_image_names:
            for pk, name in zip(failed_public_sale_ids, failed_public_sale_image_names):
                logger.info(f"🚀\tpublic_sale_id : {pk} - {name} failed")

        if failed_public_sale_detail_ids and failed_public_sale_detail_image_names:
            for pk, name in zip(
                failed_public_sale_detail_ids, failed_public_sale_detail_image_names
            ):
                logger.info(f"🚀\tpublic_sales_detail_id : {pk} - {name} failed")

        if passed_image_names_dict:
            logger.info(f"🚀\t{passed_image_names_dict} passed")

        return public_sale_photos, public_sale_detail_photos

    def execute(self):
        logger.info(f"🚀\tInsertUploadPhotoUseCase Start - {self.client_id}")
        logger.info(f"🚀\tupload_job 위치 : {ImageHelper().get_image_upload_dir()}")
        start_time = time()

        passed_dirs = list()
        _dir = None
        total_public_sale_photos = 0
        total_public_sale_detail_photos = 0

        recent_public_sale_photos_info = (
            self._house_repo.get_recent_public_sale_photos()
        )
        recent_public_sale_detail_photos_info = (
            self._house_repo.get_recent_public_sale_detail_photos()
        )

        if not recent_public_sale_photos_info:
            public_sale_photos_start_idx = 1
        else:
            public_sale_photos_start_idx = recent_public_sale_photos_info.id + 1

        if not recent_public_sale_detail_photos_info:
            public_sale_detail_photos_start_idx = 1
        else:
            public_sale_detail_photos_start_idx = (
                recent_public_sale_detail_photos_info.id
            ) + 1

        upload_list: List[Dict] = list()
        for (roots, dirs, file_names) in os.walk(ImageHelper().get_image_upload_dir()):
            entry = []

            # roots 기준 1 depth 하위 dir
            _dir = roots.split(r"/")[-1]
            if "(" in _dir and ")" in _dir:
                if len(file_names) > 0:
                    for file_name in file_names:
                        entry.append(file_name)

                    upload_list.append(
                        self.collect_file_list(dir_name=_dir, file_list=entry)
                    )
            elif _dir == "upload_images_list":
                continue
            else:
                passed_dirs.append(_dir)

        logger.info(f"🚀\tFinished collect_file_list in upload_images_list")

        for entry in upload_list:
            key = list(entry.keys())[0]
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
                total_public_sale_photos = total_public_sale_photos + len(
                    public_sale_photos
                )
            except Exception as e:
                logger.error(f"insert_images_to_public_sale_photos error : {e}")
                exit(os.EX_OK)

            # Bulk insert public_sale_detail_photos
            try:
                self._house_repo.insert_images_to_public_sale_detail_photos(
                    create_list=public_sale_detail_photos
                )
                total_public_sale_detail_photos = total_public_sale_detail_photos + len(
                    public_sale_detail_photos
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

        if passed_dirs:
            for name in passed_dirs:
                logger.info(f"🚀\tPassed_dir_list : {name} passed")

        logger.info(
            f"🚀\tInsertUploadPhotoUseCase - Done! "
            f"public_sale_photos: {total_public_sale_photos} upserted, "
            f"public_sale_detail_photos: {total_public_sale_detail_photos} upserted, "
            f"records: {time() - start_time} secs"
        )
        exit(os.EX_OK)


class ReplacePublicToPrivateUseCase(BaseHouseWorkerUseCase):
    """
        - What : 분양 마감 건에 대하여 매매 매물로 전환 배치
        - When : 매월 1일 한번 시행
        1. Target : 모든 public_sales (분양매물)에 대하여 마감된 매물
            - move_in_year, move_in_month (입주가능년월)을 배치 코드를 실행하는 현재 년월과 대조한다.
            - 대조시, 년도가 달라지는 경우에 주의한다 (예시 : 2021.01(현재) 2020.12 입주가능할경우)
            - 현재 년월과 비교하여 1달 이상 지났을 경우 private_sales 전환 대상
            - 주의 : 사전에 이미 전환된 private_sales가 있을 수 있다
            - -> private_sales 생성 전, 하나의 real_estates id로 public_sales와 private_sales 동시 사용중인 매물을 체크
            - 이미 private_sales가 생성되어 있는 건에 대해서는 public_ref_id를 포함한 기타 정보 업데이트 처리
        2. private_sales 전환 대상 public_sales에 대하여 private_sales 생성
            - public_sales is_available = False 처리
            - 기존 분양 정보를 참고하여 새로운 private_sales 생성
            - 이때, private_sales.public_ref_id에 전환 전 public_sales id 저장
            - 막 매매 전환된 건이므로 구체적 매매 정보(private_sale_details)는 아예 없는 상태
    """

    def _get_replace_target(
        self, public_sales: List[PublicSaleEntity]
    ) -> List[PublicSaleEntity]:
        replace_target = list()
        for public_sale in public_sales:
            result = HouseHelper().is_public_to_private_target(
                move_in_year=public_sale.move_in_year,
                move_in_month=public_sale.move_in_month,
            )
            if result == ReplacePublicToPrivateSalesEnum.YES.value:
                replace_target.append(public_sale)

        return replace_target

    def _make_disable_update_list_to_replace_target(
        self, target_list: List[PublicSaleEntity]
    ) -> List[dict]:
        result_dict_list = list()
        for target in target_list:
            result_dict_list.append(
                {
                    "id": target.id,
                    "is_available": False,
                    "updated_at": get_server_timestamp(),
                }
            )
        return result_dict_list

    def _make_replace_private_sales_create_list(
        self,
        target_list: List[PublicSaleEntity],
        avoid_pk_list: List[int],
        start_pk: int,
    ) -> List[dict]:
        result_dict_list = list()
        start_idx = start_pk

        for target in target_list:
            if avoid_pk_list:
                if target.real_estate_id in avoid_pk_list:
                    continue
                else:
                    result_dict_list.append(
                        {
                            "id": start_idx,
                            "real_estate_id": target.real_estate_id,
                            "name": target.name,
                            "building_type": BuildTypeEnum.APARTMENT,
                            "move_in_year": HouseHelper().add_move_in_year_and_move_in_month_to_str(
                                move_in_year=target.move_in_year,
                                move_in_month=target.move_in_month,
                            ),
                            "construct_company": target.construct_company
                            if target.construct_company
                            else None,
                            "supply_household": target.supply_household
                            if target.supply_household
                            else None,
                            "is_available": True,
                            "public_ref_id": target.id,
                            "created_at": get_server_timestamp(),
                            "updated_at": get_server_timestamp(),
                        }
                    )
                    start_idx = start_idx + 1
            else:
                result_dict_list.append(
                    {
                        "id": start_pk,
                        "real_estate_id": target.real_estate_id,
                        "name": target.name,
                        "building_type": BuildTypeEnum.APARTMENT,
                        "move_in_year": str(target.move_in_year)
                        + str(target.move_in_month),
                        "construct_company": target.construct_company
                        if target.construct_company
                        else None,
                        "supply_household": target.supply_household
                        if target.supply_household
                        else None,
                        "is_available": True,
                        "public_ref_id": target.id,
                        "created_at": get_server_timestamp(),
                        "updated_at": get_server_timestamp(),
                    }
                )
                start_idx = start_idx + 1

        return result_dict_list

    def _make_update_list_for_update_public_ref_id(
        self, target_list: List[CheckIdsRealEstateEntity]
    ) -> List[dict]:
        result_dict_list = list()
        for target in target_list:
            result_dict_list.append(
                {
                    "id": target.private_sale_id,
                    "supply_household": target.supply_household,
                    "construct_company": target.construct_company,
                    "move_in_year": target.move_in_year,
                    "public_ref_id": target.public_sale_id,
                    "updated_at": get_server_timestamp(),
                }
            )
        return result_dict_list

    def execute(self):
        logger.info(f"🚀\tReplacePublicToPrivateUseCase Start - {self.client_id}")
        start_time = time()

        # public_sales: 이용 가능한 분양 타입 매물
        public_sales = self._house_repo.get_target_list_of_public_sales()

        if not public_sales:
            logger.info(
                f"🚀\t [get_target_list_of_public_sales] - Nothing to replace target "
            )
            exit(os.EX_OK)

        # replace_targets: 매매 전환 대상 리스트
        replace_targets = self._get_replace_target(public_sales=public_sales)

        if not replace_targets:
            logger.info(f"🚀\t [get_replace_target] - Nothing to replace target ")
            exit(os.EX_OK)

        private_sale_start_idx = 1
        recent_private_sale_info = self._house_repo.get_recent_private_sales()
        if recent_private_sale_info:
            private_sale_start_idx = recent_private_sale_info.id + 1

        target_ids = [target.real_estate_id for target in replace_targets]

        # 타겟 중 이미 매매 전환되어 private_sales 가 생성된 건이 있는지 확인
        already_created_private_sales = self._house_repo.get_private_sales_have_real_estates_both_public_and_private(
            target_ids
        )

        # avoid_pk_list : public, private 양쪽 모두 가지고 있는 real_estate_id_list
        avoid_pk_list = [
            target.real_estate_id for target in already_created_private_sales
        ]

        # 이미 매매 전환되어 private_sales 건에 대한 public_ref_id update 처리
        real_estates_with_fks = self._house_repo.get_real_estates_have_both_public_and_private(
            avoid_pk_list
        )

        public_ref_id_update_list = self._make_update_list_for_update_public_ref_id(
            real_estates_with_fks
        )

        try:
            self._house_repo.bulk_update_private_sales(
                update_list=public_ref_id_update_list
            )
        except Exception as e:
            logger.error(f"🚀\t [bulk_update_private_sales] - Error : {e} ")
            exit(os.EX_OK)

        # 최초 생성 매매건 - 이미 생성되어 있는 real_estate_id는 패스하고 insert 진행
        create_list = self._make_replace_private_sales_create_list(
            target_list=replace_targets,
            avoid_pk_list=avoid_pk_list,
            start_pk=private_sale_start_idx,
        )

        try:
            self._house_repo.bulk_create_private_sale(create_list=create_list)
        except Exception as e:
            logger.error(f"🚀\t [bulk_update_public_sales] - Error : {e} ")
            exit(os.EX_OK)

        # bulk_update : 전환 대상 public_sales is_available = False 처리
        update_list = self._make_disable_update_list_to_replace_target(
            target_list=replace_targets
        )
        try:
            self._house_repo.bulk_update_public_sales(update_list=update_list)
        except Exception as e:
            logger.error(f"🚀\t [bulk_update_public_sales] - Error : {e} ")
            exit(os.EX_OK)

        if avoid_pk_list:
            logger.info(
                f"🚀\t [bulk_create_private_sale] - Done! "
                f"{len(replace_targets) - len(avoid_pk_list)} / {len(replace_targets)} created, "
                f"records: {time() - start_time} secs"
            )
        else:
            logger.info(
                f"🚀\t [bulk_create_private_sale] - Done! "
                f"{len(replace_targets)} created, "
                f"records: {time() - start_time} secs"
            )

        exit(os.EX_OK)


class CheckNotUploadedPhotoUseCase(BaseHouseWorkerUseCase):
    def execute(self):
        target_dir = ImageHelper().get_image_upload_dir()
        logger.info(f"🚀\tCheckNotUploadedPhotoUseCase Start - {self.client_id}")
        logger.info(f"🚀\tCheck_photos 위치 : {target_dir}")
        start_time = time()

        collector = ImageNameCollector(target_dir=target_dir)

        collector.get_file_list()

        dir_name_list = list()

        for elm in collector.collect_dict_list:
            keys = elm.keys()
            dir_name_list.append(*keys)

        public_sale_ids, passed_dirs = collector.get_public_sale_photos_ids(
            dir_name_list=dir_name_list
        )

        not_uploaded_public_sale_ids = list()

        for id_ in public_sale_ids:
            if not self._house_repo.is_exists_public_sale_photos(id_):
                not_uploaded_public_sale_ids.append(id_)

        logger.info(
            f"🚀\tCheckNotUploadedPhotoUseCase - Done! \n"
            f"public_sale_id: {not_uploaded_public_sale_ids} not uploaded photos, "
            f"({len(not_uploaded_public_sale_ids)}/ {len(public_sale_ids)})\n"
            f"passed_dirs: {passed_dirs}\n"
            f"records: {time() - start_time} secs"
        )

        emoji = "🚀"

        self.send_slack_message(
            title=f"{emoji} [CheckNotUploadedPhotoUseCase] >>> 업로드 누락 이미지 체크",
            message=f"CheckNotUploadedPhotoUseCase : Finished !! \n "
            f"records: {time() - start_time} secs \n "
            f"public_sale_id: {not_uploaded_public_sale_ids} not uploaded photos, "
            f"({len(not_uploaded_public_sale_ids)}/ {len(public_sale_ids)}) \n",
        )

        exit(os.EX_OK)


class AddSupplyAreaUseCase(BaseHouseWorkerUseCase):
    """
        - What : 현재 실거래가에 공급면적이 존재하지 않기 때문에 건축물대장 API를 통해서 추가한다.
                 원래는 Core DB에 추가해야 하지만 현재 Sam의 리소스가 없기 때문에 Tanos에 먼저 추가하고
                 MVP 이후에 Core 쪽에 추가한 후 해당 Topic은 삭제한다.
        - When : 데일리 실거래가가 들어온 직후 Tanos 배치가 돌기전에 돌려야 한다.
        - API Param
            1. ServiceKey : dbNxRdjZCqBvSjcfDHnxPgUm0CXIjGhNHSAlbvBxI0BvOu3dpL8t%2FFQ%2BDRE%2FoKPw61Nm0gHxqYTlYEgDxz37aw%3D%3D
            2. sigunguCd : front_legal_code
            3. bjdongCd : back_legal_code
            4. bun : land_number
            5. ji : land_number
            6. numOfRows : 10

        - 삭제필요 코드는 전부 옆에와 같이 todo를 달아놈 -> todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
    """

    def execute(self):
        logger.info(f"🚀\tAddSupplyAreaUseCase Start - {self.client_id}")
        start_time = time()
        emoji = "🚀"

        # bulk insert summary_create_list to temp_summary_supply_area_api
        # self._house_repo.create_summary_success_list_to_temp_summary()
        #
        # logger.info(
        #     f"🚀\tAddSupplyAreaUseCase - Done! \n"
        #     f"records: {time() - start_time} secs \n"
        # )
        # exit(os.EX_OK)

        # private_sales 중 아파트,오피스텔 건만 데이터를 조회한다.
        target_list: List[
            AddSupplyAreaEntity
        ] = self._house_repo.get_target_of_add_to_supply_area()
        last_target_id = None  # 실패로그를 위한 변수
        create_list = list()
        summary_failure_list = list()
        summary_failure_log_list = list()
        count = 0  # 로그 확인용 변수

        if not target_list:
            logger.info(
                f"🚀\tAddSupplyAreaUseCase - Done! \n"
                f"last_real_estate_id: {last_target_id} \n"
                f"records: {time() - start_time} secs \n"
                f"(총 타겟: 0 / 실패: 0)"
            )

            self.send_slack_message(
                title=f"{emoji} [AddSupplyAreaUseCase] >>> 공급면적 추가 배치",
                message=f"AddSupplyAreaUseCase : Finished !! \n "
                f"records: {time() - start_time} secs \n "
                f"(총 타겟: 0 / 실패: 0)",
            )
            exit(os.EX_OK)

        url = "http://apis.data.go.kr/1613000/BldRgstService_v2/getBrExposPubuseAreaInfo?ServiceKey=dbNxRdjZCqBvSjcfDHnxPgUm0CXIjGhNHSAlbvBxI0BvOu3dpL8t%2FFQ%2BDRE%2FoKPw61Nm0gHxqYTlYEgDxz37aw%3D%3D"

        try:
            for target in target_list:
                count += 1

                last_target_id = target.req_real_estate_id
                req_land_number = target.req_land_number
                land_number = req_land_number.split("-")
                ji = None

                if len(land_number) > 1:
                    bun = land_number[0].zfill(4)
                    ji = land_number[1].zfill(4)
                else:
                    bun = land_number[0].zfill(4)

                num_of_rows = 10000
                page_no = 1
                r_num = None

                while True:
                    start_call_time = time()

                    request_param = "&numOfRows={}&pageNo={}&sigunguCd={}&bjdongCd={}&bun={}".format(
                        num_of_rows,
                        page_no,
                        target.req_front_legal_code,
                        target.req_back_legal_code,
                        bun,
                    )
                    if ji:
                        request_param += "&ji={}".format(ji)

                    try:
                        response = requests.get(
                            url=url + request_param,
                            headers={
                                "Content-Type": "application/json; charset=utf8",
                                "Cache-Control": "no-cache",
                            },
                        )
                    except Exception as e:
                        logger.info(
                            f"☠️\tAddSupplyAreaUseCase - Response Failure! \n"
                            f"exception : {str(e)} \n"
                        )
                        sleep(5)
                        continue

                    logger.info(
                        f"🚀\tcall API!\n"
                        f"count: {count} \n"
                        f"real_estate_id: {target.req_real_estate_id} \n"
                        f"page_no: {page_no} / front_legal_code: {target.req_front_legal_code} / back_legal_code: {target.req_back_legal_code} \n"
                        f"bun: {bun} / ji: {ji} \n"
                        f"records: {time() - start_call_time} secs"
                    )

                    if response.status_code == 200:
                        xpars = xmltodict.parse(response.text)
                        json_data = json.dumps(xpars["response"]["body"])
                        data = json.loads(json_data)

                        if not data["items"]:
                            summary_failure_list.append(
                                dict(
                                    real_estate_id=target.req_real_estate_id,
                                    real_estate_name=target.req_real_estate_name,
                                    private_sale_id=target.req_private_sale_id,
                                    private_sale_name=target.req_private_sale_name,
                                    success_yn=False,
                                )
                            )
                            summary_failure_log_list.append(target.req_real_estate_id)
                            break

                        total_count = data["totalCount"]

                        item_type = isinstance(
                            data["items"]["item"], dict
                        )  # list에 담겨져오는 것이 대부분이나 일부는 json 형식으로 내려옴
                        if item_type:
                            item = data["items"]["item"]
                            resp_dong_nm = item["dongNm"]
                            resp_ho_nm = item["hoNm"]
                            resp_bld_nm = item["bldNm"]  # 아파트 이름
                            resp_flr_no_nm = item["flrNoNm"]  # 층 이름
                            resp_area = item["area"]  # 공급면적
                            resp_jibun_address = item["newPlatPlc"]  # 지번 주소
                            resp_road_address = item["platPlc"]  # 도로명 주소
                            resp_etc_purps = item[
                                "etcPurps"
                            ]  # 아파트/ 오피스텔 / 펌프실 / 관리 / 주차장 ...
                            resp_expos_pubuse_gb_cd_nm = item[
                                "exposPubuseGbCdNm"
                            ]  # 전유 / 공용
                            resp_main_atch_gb_cd = item["mainAtchGbCd"]  # 0 / 1
                            resp_main_atch_gb_cd_nm = item[
                                "mainAtchGbCdNm"
                            ]  # 주건축물 / 부속건출물, ....
                            resp_main_purps_cd = item[
                                "mainPurpsCd"
                            ]  # 02001 / 02002~02006 (부속건축물)

                            # 1부터 시작
                            r_num = item["rnum"]

                            # if not (resp_main_atch_gb_cd == "0" and resp_main_purps_cd == "02001"):
                            #     continue

                            if (
                                resp_main_atch_gb_cd != "0"
                                and target.req_private_building_type.value == "아파트"
                            ):
                                continue

                            create_dict = dict(
                                req_front_legal_code=target.req_front_legal_code,
                                req_back_legal_code=target.req_back_legal_code,
                                req_land_number=target.req_land_number,
                                req_real_estate_id=target.req_real_estate_id,
                                req_real_estate_name=target.req_real_estate_name,
                                req_private_sale_id=target.req_private_sale_id,
                                req_private_sale_name=target.req_private_sale_name,
                                req_private_building_type=target.req_private_building_type.value,
                                req_jibun_address=target.req_jibun_address,
                                req_road_address=target.req_road_address,
                                resp_rnum=r_num,
                                resp_total_count=total_count,
                                resp_name=resp_bld_nm,
                                resp_dong_nm=resp_dong_nm,
                                resp_ho_nm=resp_ho_nm,
                                resp_flr_no_nm=resp_flr_no_nm,
                                resp_area=resp_area,
                                resp_jibun_address=resp_jibun_address,
                                resp_road_address=resp_road_address,
                                resp_etc_purps=resp_etc_purps,
                                resp_expos_pubuse_gb_cd_nm=resp_expos_pubuse_gb_cd_nm,
                                resp_main_atch_gb_cd=resp_main_atch_gb_cd,
                                resp_main_atch_gb_cd_nm=resp_main_atch_gb_cd_nm,
                                resp_main_purps_cd=resp_main_purps_cd,
                                update_need=True,
                            )

                            create_list.append(create_dict)
                        else:
                            for item in data["items"]["item"]:
                                resp_dong_nm = item["dongNm"]
                                resp_ho_nm = item["hoNm"]
                                resp_bld_nm = item["bldNm"]  # 아파트 이름
                                resp_flr_no_nm = item["flrNoNm"]  # 층 이름
                                resp_area = item["area"]  # 공급면적
                                resp_jibun_address = item["newPlatPlc"]  # 지번 주소
                                resp_road_address = item["platPlc"]  # 도로명 주소
                                resp_etc_purps = item[
                                    "etcPurps"
                                ]  # 아파트/ 오피스텔 / 펌프실 / 관리 / 주차장 ...
                                resp_expos_pubuse_gb_cd_nm = item[
                                    "exposPubuseGbCdNm"
                                ]  # 전유 / 공용
                                resp_main_atch_gb_cd = item["mainAtchGbCd"]  # 0 / 1
                                resp_main_atch_gb_cd_nm = item[
                                    "mainAtchGbCdNm"
                                ]  # 주건축물 / 부속건출물, ....
                                resp_main_purps_cd = item[
                                    "mainPurpsCd"
                                ]  # 02001 / 02002~02006 (부속건축물)

                                # 1부터 시작
                                r_num = item["rnum"]

                                # if not (resp_main_atch_gb_cd == "0" and resp_main_purps_cd == "02001"):
                                #     continue

                                if (
                                    resp_main_atch_gb_cd != "0"
                                    and target.req_private_building_type.value == "아파트"
                                ):
                                    continue

                                create_dict = dict(
                                    req_front_legal_code=target.req_front_legal_code,
                                    req_back_legal_code=target.req_back_legal_code,
                                    req_land_number=target.req_land_number,
                                    req_real_estate_id=target.req_real_estate_id,
                                    req_real_estate_name=target.req_real_estate_name,
                                    req_private_sale_id=target.req_private_sale_id,
                                    req_private_sale_name=target.req_private_sale_name,
                                    req_private_building_type=target.req_private_building_type.value,
                                    req_jibun_address=target.req_jibun_address,
                                    req_road_address=target.req_road_address,
                                    resp_rnum=r_num,
                                    resp_total_count=total_count,
                                    resp_name=resp_bld_nm,
                                    resp_dong_nm=resp_dong_nm,
                                    resp_ho_nm=resp_ho_nm,
                                    resp_flr_no_nm=resp_flr_no_nm,
                                    resp_area=resp_area,
                                    resp_jibun_address=resp_jibun_address,
                                    resp_road_address=resp_road_address,
                                    resp_etc_purps=resp_etc_purps,
                                    resp_expos_pubuse_gb_cd_nm=resp_expos_pubuse_gb_cd_nm,
                                    resp_main_atch_gb_cd=resp_main_atch_gb_cd,
                                    resp_main_atch_gb_cd_nm=resp_main_atch_gb_cd_nm,
                                    resp_main_purps_cd=resp_main_purps_cd,
                                    update_need=True,
                                )

                                create_list.append(create_dict)

                        if int(r_num) < int(total_count):
                            page_no += 1
                            continue

                        break

                # bulk insert to temp_supply_area_api
                if create_list:
                    self._house_repo.create_temp_supply_area_api(
                        create_list=create_list,
                        summary_failure_list=summary_failure_list,
                    )

                # bulk insert summary_failure_list to temp_summary_supply_area_api
                if summary_failure_list:
                    self._house_repo.create_summary_failure_list_to_temp_summary(
                        create_list=summary_failure_list
                    )

                create_list = list()
                summary_failure_list = list()

            # bulk insert summary_create_list to temp_summary_supply_area_api
            self._house_repo.create_summary_success_list_to_temp_summary()

        except Exception as e:
            logger.info(
                f"☠️\tAddSupplyAreaUseCase - Failure! \n"
                f"exception : {str(e)} \n"
                f"last_real_estate_id: {last_target_id} \n"
                f"records: {time() - start_time} secs"
            )

        logger.info(
            f"🚀\tAddSupplyAreaUseCase - Done! \n"
            f"last_real_estate_id: {last_target_id} \n"
            f"records: {time() - start_time} secs \n"
            f"(총 타겟: {len(target_list)} / 실패: {len(summary_failure_log_list)}) \n"
            f"summary_failure_log_list(real_estate_id): {summary_failure_log_list}"
        )

        self.send_slack_message(
            title=f"{emoji} [AddSupplyAreaUseCase] >>> 공급면적 추가 배치",
            message=f"AddSupplyAreaUseCase : Finished !! \n "
            f"records: {time() - start_time} secs \n "
            f"(총 타겟: {len(target_list)} / 실패: {len(summary_failure_log_list)}) \n"
            f"summary_failure_log_list(real_estate_id): {summary_failure_log_list}",
        )

        exit(os.EX_OK)


class BindSupplyAreaUseCase(BaseHouseWorkerUseCase):
    """
        - What : 현재 실거래가에 공급면적이 존재하지 않기 때문에 건축물대장 API를 통해서 추가한다.
                 원래는 Core DB에 추가해야 하지만 현재 Sam의 리소스가 없기 때문에 Tanos에 먼저 추가하고
                 MVP 이후에 Core 쪽에 추가한 후 해당 Topic은 삭제한다.
        - When : 데일리 실거래가가 들어온 직후 Tanos 배치가 돌기전에 돌려야 한다.
        - 삭제필요 코드는 전부 옆에와 같이 todo를 달아놈 -> todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
    """

    def execute(self):
        logger.info(f"🚀\tBindSupplyAreaUseCase Start - {self.client_id}")
        start_time = time()
        emoji = "🚀"

        last_target_id = None  # 실패로그를 위한 변수
        create_list = list()
        failure_list = list()

        # private_sales.create_at or updated_at이 오늘날짜인 타겟 id를 조회한다.
        target_entities: List[
            BindTargetSupplyAreaEntity
        ] = self._house_repo.get_private_sales_target_ids_for_supply_area()

        if not target_entities:
            logger.info(f"🚀\tUpdate_private_sale_ids : Nothing target_ids")
            self.send_slack_message(
                title=f"{emoji} [BindSupplyAreaUseCase] >>> 공급면적 추가 배치",
                message=f"BindSupplyAreaUseCase : Finished !! \n "
                f"records: {time() - start_time} secs \n "
                f"Update_private_sale_ids : Nothing target_ids",
            )
            exit(os.EX_OK)

        try:
            for target_entity in target_entities:
                if not target_entity.ref_summary_id:
                    failure_list.append(
                        BindFailureSupplyAreaEntity(
                            real_estate_name=target_entity.real_estate_name,
                            private_sale_name=target_entity.private_sale_name,
                            real_estate_id=target_entity.real_estate_id,
                            private_sale_id=target_entity.private_sale_id,
                            private_area=target_entity.private_area,
                            supply_area=target_entity.supply_area,
                            front_legal_code=target_entity.front_legal_code,
                            back_legal_code=target_entity.back_legal_code,
                            jibun_address=target_entity.jibun_address,
                            road_address=target_entity.road_address,
                            land_number=target_entity.land_number,
                            failure_reason="not target_entity.ref_summary_id",
                            is_done=False,
                            ref_summary_id=target_entity.ref_summary_id,
                        )
                    )
                else:
                    create_list.append(
                        BindSuccessSupplyAreaEntity(
                            real_estate_name=target_entity.real_estate_name,
                            private_sale_name=target_entity.private_sale_name,
                            real_estate_id=target_entity.real_estate_id,
                            private_sale_id=target_entity.private_sale_id,
                            private_area=target_entity.private_area,
                            supply_area=target_entity.supply_area,
                            front_legal_code=target_entity.front_legal_code,
                            back_legal_code=target_entity.back_legal_code,
                            jibun_address=target_entity.jibun_address,
                            road_address=target_entity.road_address,
                            land_number=target_entity.land_number,
                            ref_summary_id=target_entity.ref_summary_id,
                        )
                    )

            # update private_sale_details && insert to temp_success_supply_area
            # 히스토리 저장 (append insert)
            self._house_repo.create_temp_success_supply_area(
                create_list=create_list, failure_list=failure_list
            )
            # insert to temp_failure_supply_area
            # 히스토리 저장 (append insert)
            self._house_repo.create_temp_failure_supply_area(failure_list=failure_list)

        except Exception as e:
            logger.info(
                f"☠️\tBindSupplyAreaUseCase - Failure! \n"
                f"last_real_estate_id: {last_target_id} \n"
                f"records: {time() - start_time} secs"
            )

        logger.info(
            f"🚀\tBindSupplyAreaUseCase - Done! \n"
            f"last_real_estate_id: {last_target_id} \n"
            f"records: {time() - start_time} secs \n"
            f"(총 타겟: {len(target_entities)} / 실패: {len(failure_list)}) \n"
            f"summary_failure_log_list(real_estate_id): {failure_list}"
        )

        self.send_slack_message(
            title=f"{emoji} [BindSupplyAreaUseCase] >>> 공급면적 바인딩 배치",
            message=f"BindSupplyAreaUseCase : Finished !! \n "
            f"records: {time() - start_time} secs \n "
            f"(총 타겟: {len(target_entities)} / 실패: {len(failure_list)}) \n"
            f"summary_failure_log_list(real_estate_id): {failure_list}",
        )

        exit(os.EX_OK)
