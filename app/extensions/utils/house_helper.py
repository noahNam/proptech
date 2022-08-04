from typing import Optional, List

from app.extensions.utils.math_helper import MathHelper
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.enum.house_enum import (
    CalcPyoungEnum,
    PublicSaleStatusEnum,
    ReplacePublicToPrivateSalesEnum,
    CalendarYearThreshHold,
)
from core.domains.report.entity.report_entity import HouseTypeRankEntity


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
            return int(MathHelper.round(float(area) / CalcPyoungEnum.CALC_VAR.value))
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
    def public_status(cls, offer_date: str, end_date: str) -> int:
        if (
            not offer_date
            or offer_date == "0"
            or offer_date == "00000000"
            or not end_date
            or end_date == "0"
            or end_date == "00000000"
        ):
            return PublicSaleStatusEnum.UNKNOWN.value

        today = get_server_timestamp().strftime("%Y%m%d")

        if today < offer_date:
            return PublicSaleStatusEnum.BEFORE_OPEN.value
        elif offer_date <= today <= end_date:
            return PublicSaleStatusEnum.IS_RECEIVING.value
        elif end_date < today:
            return PublicSaleStatusEnum.IS_CLOSED.value
        else:
            return PublicSaleStatusEnum.UNKNOWN.value

    @classmethod
    def convert_avg_competition(cls, avg_competition: Optional[int]) -> str:
        if avg_competition == 0:
            return "미달"
        elif not avg_competition:
            return "-"

        return "{}:1".format(avg_competition)

    @classmethod
    def convert_min_score(cls, min_score: Optional[int]) -> str:
        if min_score == 0:
            return "미달"
        elif not min_score:
            return "-"

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

    @classmethod
    def add_move_in_year_and_move_in_month_to_str(
        cls, move_in_year: int, move_in_month: int
    ) -> Optional[str]:
        """
            ex) 2021, 1 -> str(202101)
        """
        if not isinstance(move_in_year, int) or not isinstance(move_in_month, int):
            return None

        if 0 < move_in_month < 10:
            month_to_str = "0" + str(move_in_month)
        else:
            month_to_str = str(move_in_month)

        year_to_str = str(move_in_year)

        return year_to_str + month_to_str

    @classmethod
    def sort_predicted_competition(
        cls, house_type_ranks: List[HouseTypeRankEntity]
    ) -> None:
        end = len(house_type_ranks) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                if house_type_ranks[i].rank > house_type_ranks[i + 1].rank:
                    house_type_ranks[i], house_type_ranks[i + 1] = (
                        house_type_ranks[i + 1],
                        house_type_ranks[i],
                    )
                    last_swap = i
            end = last_swap

    @classmethod
    def convert_contract_amount_to_integer(
        cls, contract_amount: Optional[float]
    ) -> Optional[int]:
        return int(contract_amount * 100) if contract_amount else None
