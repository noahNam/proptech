from typing import Optional

from app.extensions.utils.math_helper import MathHelper
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.enum.house_enum import CalcPyoungEnum, PublicSaleStatusEnum


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
