from typing import Optional

from app.extensions.utils.math_helper import MathHelper
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.enum.house_enum import (
    CalcPyoungEnum,
    PublicSaleStatusEnum,
    ReplacePublicToPrivateSalesEnum,
    CalendarYearThreshHold,
)


class HouseHelper:
    """
        공급면적이 있는 경우는 정확 값 내려주고 없는 경우는 임의로 계산한 값을 내려준다.
    """

    @classmethod
    def convert_area_to_pyoung(cls, area: Optional[float]) -> Optional[int]:
        """
            1평 = 3.3058 (제곱미터)
        """

        if area:
            return int(MathHelper.round(area / CalcPyoungEnum.CALC_VAR.value))
        else:
            return None

    @classmethod
    def convert_area_to_temp_pyoung(cls, area: Optional[float]) -> Optional[int]:
        if area:
            return int(
                MathHelper.round(
                    (area * CalcPyoungEnum.TEMP_CALC_VAR.value)
                    / CalcPyoungEnum.CALC_VAR.value
                )
            )
        else:
            return None

    @classmethod
    def public_status(cls, offer_date: str, subscription_end_date: str) -> int:
        if (
            not offer_date
            or offer_date == "0"
            or offer_date == "00000000"
            or not subscription_end_date
            or subscription_end_date == "0"
            or subscription_end_date == "00000000"
        ):
            return PublicSaleStatusEnum.UNKNOWN.value

        today = get_server_timestamp().strftime("%Y%m%d")

        if today < offer_date:
            return PublicSaleStatusEnum.BEFORE_OPEN.value
        elif offer_date <= today <= subscription_end_date:
            return PublicSaleStatusEnum.IS_RECEIVING.value
        elif subscription_end_date < today:
            return PublicSaleStatusEnum.IS_CLOSED.value
        else:
            return PublicSaleStatusEnum.UNKNOWN.value

    @classmethod
    def convert_avg_competition(cls, avg_competition: Optional[int]) -> str:
        if not avg_competition or avg_competition == 0:
            return "미달"
        return "{}:1".format(avg_competition)

    @classmethod
    def convert_min_score(cls, min_score: Optional[int]) -> str:
        if not min_score or min_score == 0:
            return "미달"
        return "{}점".format(min_score)

    @classmethod
    def is_public_to_private_target(cls, move_in_year: int, move_in_month: int) -> int:
        """
            판별 가능 연도 범위
            CalendarYearThreshHold Enum MIN_YEAR ~ MAX_YEAR (현재 2017 ~ 2030 (App 달력 표시 가능 연도 범위))
            범위 조절해야 할 경우 CalendarYearThreshHold Enum 값 수정해주세요
        """
        if (
            not isinstance(move_in_year, int)
            or not isinstance(move_in_month, int)
            or (move_in_month < 1)
            or (move_in_month > 12)
            or (move_in_year < CalendarYearThreshHold.MIN_YEAR.value)
            or (move_in_year > CalendarYearThreshHold.MAX_YEAR.value)
        ):
            return ReplacePublicToPrivateSalesEnum.UNKNOWN.value

        today = get_server_timestamp()

        if today.year < move_in_year:
            return ReplacePublicToPrivateSalesEnum.NO.value
        elif today.year == move_in_year:
            if today.month > move_in_month:
                return ReplacePublicToPrivateSalesEnum.YES.value
            else:
                return ReplacePublicToPrivateSalesEnum.NO.value
        elif today.year > move_in_year:
            return ReplacePublicToPrivateSalesEnum.YES.value
        else:
            return ReplacePublicToPrivateSalesEnum.UNKNOWN.value
