from typing import Optional

from app.extensions.utils.math_helper import MathHelper
from core.domains.house.enum.house_enum import CalcPyoungEnum


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
                MathHelper.round((area * CalcPyoungEnum.TEMP_CALC_VAR.value) / CalcPyoungEnum.CALC_VAR.value)
            )
        else:
            return None
