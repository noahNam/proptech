from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class InterestHouseEntity(BaseModel):
    id: int
    user_id: int
    house_id: int
    type: int
    is_like: bool
    created_at: datetime
    updated_at: datetime


class RealEstateEntity(BaseModel):
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
    # coordinates: Point
    # to_entity(): coordinates 대신 아래 위경도 값 사용
    latitude: float
    longitude: float


class PublicSaleDetailEntity(BaseModel):
    id: int
    public_sales_id: int
    private_area: float
    supply_area: float
    supply_price: int
    acquisition_tax: int


class PublicSalePhotoEntity(BaseModel):
    id: int
    public_sales_id: int
    file_name: str
    path: str
    extension: str
    created_at: datetime
    updated_at: datetime


class PublicSaleEntity(BaseModel):
    id: int
    real_estate_id: int
    name: str
    region: str
    housing_category: Enum
    rent_type: Enum
    trade_type: Enum
    construct_company: str
    supply_household: int
    is_available: bool
    offer_date: str
    subscription_start_date: str
    subscription_end_date: str
    special_supply_date: str
    special_supply_etc_date: str
    first_supply_date: str
    first_supply_etc_date: str
    second_supply_date: str
    second_supply_etc_date: str
    notice_winner_date: str
    contract_start_date: str
    contract_end_date: str
    move_in_year: int
    move_in_month: int
    min_down_payment: int
    max_down_payment: int
    down_payment_ratio: int
    reference_url: str
    created_at: datetime
    updated_at: datetime
    public_sale_photos: PublicSalePhotoEntity = None
    public_sale_details: List[PublicSaleDetailEntity] = None

    class Config:
        use_enum_values = True


class PublicSalePushEntity(BaseModel):
    id: int
    name: str
    region: str
    message_type: str = None


class PrivateSaleEntity(BaseModel):
    id: int
    real_estate_id: int
    private_area: float
    supply_area: float
    contract_date: str
    deposit_price: int
    rent_price: int
    trade_price: int
    floor: int
    trade_type: Enum
    building_type: Enum
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class AdministrativeDivisionEntity(BaseModel):
    id: int
    name: str
    short_name: str
    real_trade_price: int
    real_rent_price: int
    real_deposit_price: int
    public_sale_price: int
    level: Enum
    # coordinates: Point
    # to_entity(): coordinates 대신 아래 위경도 값 사용
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class BoundingRealEstateEntity(BaseModel):
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
    latitude: float
    longitude: float
    private_sales: List[PrivateSaleEntity] = None
    public_sales: PublicSaleEntity = None

    class Config:
        use_enum_values = True
