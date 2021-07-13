from typing import Optional, List

from pydantic import BaseModel

from core.domains.house.entity.house_entity import PrivateSaleEntity, RealEstateEntity


class CoordinatesRangeDto(BaseModel):
    """
        위도: Y (127.xxx),
        경도: X (37.xxx)
    """
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    level: int


class UpsertInterestHouseDto(BaseModel):
    user_id: int
    house_id: int
    type: int
    is_like: bool
