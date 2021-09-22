import os
import sys

import inject
import requests
import sentry_sdk

from app.extensions.utils.log_helper import logger_
from core.domains.house.entity.house_entity import PrivateSaleDetailEntity
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

    def execute(self):
        logger.info(f"🚀\tPreCalculateAverage Start - {self.client_id}")
        try:
            logger.info(f"🚀\tupdate_private_sale_avg_trade_price Start")
            for idx in range(1000):
                recent_info: PrivateSaleDetailEntity \
                    = self._house_repo.get_recently_contracted_private_sale_details(private_sales_id=idx)

                date_filters = self._house_repo.get_pre_calc_avg_date_filters(date_from=recent_info.contract_date)
                trade_price_info: list = self._house_repo.get_pre_calc_avg_trade_price_target_of_private_sales(
                    private_sales_id=idx, date_filters=date_filters
                )

                # trade_price_info : (supply_area, avg_trade_price)
                for elm in trade_price_info:
                    pyoung = self._house_repo._convert_supply_area_to_pyoung_number(
                        supply_area=elm[0]
                    )
                    if self._house_repo.is_exists_private_sale_avg_prices(
                        private_sales_id=idx, pyoung_number=pyoung
                    ):
                        self._house_repo.update_private_sale_avg_trade_price(
                            private_sales_id=idx, pyoung_number=pyoung
                        )
                    self._house_repo.create_private_sale_avg_trade_price(
                        private_sales_id=idx, pyoung_number=pyoung
                    )

        except Exception as e:
            logger.error(f"🚀\tupdate_private_sale_avg_trade_price Error - {e}")
            self.send_slack_message(
                message=f"🚀\tupdate_private_sale_avg_trade_price Error - {e}"
            )
            sentry_sdk.capture_exception(e)
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
