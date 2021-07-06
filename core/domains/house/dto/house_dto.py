from datetime import datetime, date
from typing import Optional, List

from geojson_pydantic import Point
from pydantic import BaseModel

from core.domains.house.entity.house_entity import PublicSaleDetailEntity, PublicSalePhotoEntity, \
    PrivateSaleEntity


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


class PublicSaleDto(BaseModel):
    id: int
    real_estate_id: int
    name: str
    region: str
    housing_category: str
    rent_type: str
    trade_type: str
    construct_company: str
    supply_household: int
    is_available: bool
    offer_date: date
    subscription_start_date: date
    subscription_end_date: date
    special_supply_date: date
    special_supply_etc_date: date
    first_supply_date: date
    first_supply_etc_date: date
    second_supply_date: date
    second_supply_etc_date: date
    notice_winner_date: date
    contract_start_date: date
    contract_end_date: date
    move_in_year: int
    move_in_month: int
    min_down_payment: int
    max_down_payment: int
    down_payment_ratio: int
    reference_url: str
    created_at: datetime
    updated_at: datetime
    public_sale_details: List[PublicSaleDetailEntity] = None
    public_sale_photos: PublicSalePhotoEntity = None


class BoundingRealEstateDto(BaseModel):
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
    private_sales: List[PrivateSaleEntity] = None
    public_sales: List[PublicSaleDto] = None
