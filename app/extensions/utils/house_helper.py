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
        """
            todo: 리펙토링 필요, HouseRepository()._get_status() 로직과 겹침
        """
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
        """
            @Harry 아래 잘못되었는데 같은 로직 쓴 부분 찾아서 수정해주세요(주석처리 부분). + 입주년,입주월 int 타입인데 어떤 이유였죠? + PublicSaleStatusEnum.UNKNOWN.value 일때 front에서 어떻게 처리할지 협의됏나요?

                    입주자 모집공고일                       청약 마감일                               입주일
            |--- 분양예정 ---|-------------분양 중--------------|---------------분양 완료-------------|--------매매------> 
                                                                                              입주월말일기준(ex: 202109 -> 202110부터 매매가능)
        """
        # if today < self.subscription_start_date:
        #     return PublicSaleStatusEnum.BEFORE_OPEN.value
        # elif self.subscription_start_date <= today <= self.subscription_end_date:
        #     return PublicSaleStatusEnum.IS_RECEIVING.value
        # elif self.subscription_end_date < today:
        #     return PublicSaleStatusEnum.IS_CLOSED.value
        # else:
        #     return PublicSaleStatusEnum.UNKNOWN.value
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
