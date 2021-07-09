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


class RealEstateDto(BaseModel):
    # id: int
    # name: str
    # road_address: str
    # jibun_address: str
    # si_do: str
    # si_gun_gu: str
    # dong_myun: str
    # ri: str
    # road_name: str
    # road_number: str
    # land_number: str
    # is_available: bool
    # latitude: float
    # longitude: float
    real_estate: RealEstateEntity
    private_sales: List[PrivateSaleEntity] = None

    class Config:
        orm_mode = True
