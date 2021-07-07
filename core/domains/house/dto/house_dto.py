from datetime import datetime, date
from typing import Optional, List

from geojson_pydantic import Point
from pydantic import BaseModel

from core.domains.house.entity.house_entity import PublicSaleDetailEntity, PublicSalePhotoEntity, \
    PrivateSaleEntity, RealEstateEntity


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
    public_sale_photos: PublicSalePhotoEntity = set()


class BoundingPrivateSalesDto(BaseModel):
    real_estates: RealEstateEntity = set()
    latitude: float = set()
    longitude: float = set()
    private_sales: List[PrivateSaleEntity] = None


class BoundingPublicSalesDto(BaseModel):
    real_estates: RealEstateEntity = set()
    latitude: float = set()
    longitude: float = set()
    public_sales: List[PublicSaleDto] = set()


class BoundingDataDto(BaseModel):
    real_estates: RealEstateEntity = None
    latitude: float
    longitude: float
    # private_sales: Optional[List[PrivateSaleEntity]] = None
    # public_sales: Optional[List[PublicSaleDto]] = set()


class BoundingOuterDto(BaseModel):
    data: List[BoundingDataDto]
