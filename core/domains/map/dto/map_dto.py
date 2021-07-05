from datetime import datetime
from typing import Optional, List

from geojson_pydantic import Point
from pydantic import BaseModel

from core.domains.map.entity.map_entity import RealEstateEntity, RealTradeEntity, PreSaleEntity, \
    SubscriptionScheduleEntity


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


class MapPreSaleDto(BaseModel):
    id: int
    real_estate_id: int
    name: str
    region: str
    housing_category: str
    rent_type: str
    trade_type: str
    construct_company: str
    housing_type: str
    supply_price: int
    supply_area: float
    supply_household: int
    notes: str
    is_available: bool
    created_at: datetime
    updated_at: datetime
    subscription_schedules: SubscriptionScheduleEntity


class MapBoundingDto(BaseModel):
    id: int
    name: str
    road_address: str
    jibun_address: str
    si_do: str
    si_gun_gu: str
    dong_myun: str
    ri: str
    road_name: str
    road_number: str
    land_number: str
    is_available: bool
    coordinates: Point
    latitude: float
    longitude: float
    real_trades: List[RealTradeEntity] = None
    pre_sales: List[MapPreSaleDto] = None

    class Config:
        orm_mode = True


class RealEstateWithCoordinateDto(BaseModel):
    id: int
    name: str
    road_address: str
    jibun_address: str
    si_do: str
    si_gun_gu: str
    dong_myun: str
    ri: str
    road_name: str
    road_number: str
    land_number: str
    is_available: bool
    coordinates: Point
    latitude: float
    longitude: float
