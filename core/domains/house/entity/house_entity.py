from datetime import date, datetime
from enum import Enum
from typing import List

from geojson_pydantic import Point
from pydantic import BaseModel


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


class PrivateSaleEntity(BaseModel):
    id: int
    real_estate_id: int
    private_area: float
    supply_area: float
    contract_date: date
    deposit_price: int
    rent_price: int
    trade_price: int
    floor: int
    trade_type: Enum
    building_type: Enum
    is_available: bool
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


class PublicSaleDetailEntity(BaseModel):
    id: int
    public_sales_id: int
    private_area: float
    supply_area: float
    supply_price: int


class PublicSalePhotoEntity(BaseModel):
    id: int
    public_sales_id: int
    file_name: str
    path: str
    extension: str
    created_at: datetime
    updated_at: datetime


class AdministrativeDivisionEntity(BaseModel):
    id: int
    name: str
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


class RealEstateWithPrivateSaleEntity(BaseModel):
    real_estate: RealEstateEntity
    private_sales: List[PrivateSaleEntity] = None


class RealEstateWithPublicSaleEntity(BaseModel):
    real_estate: RealEstateEntity
    public_sale: PublicSaleEntity
    public_sale_photo: PublicSalePhotoEntity
    public_sale_details: List[PublicSaleDetailEntity] = None


class BoundingEntity(BaseModel):
    private_estates: List[RealEstateWithPrivateSaleEntity] = None
    public_estates: List[RealEstateWithPublicSaleEntity] = None
