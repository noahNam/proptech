from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class InterestHouseEntity(BaseModel):
    id: int
    user_id: int
    house_id: int
    type: int
    is_like: bool
    created_at: datetime
    updated_at: datetime


class PublicSaleDetailPhotoEntity(BaseModel):
    id: int
    public_sale_details_id: int
    file_name: str
    path: str
    extension: str
    created_at: datetime
    updated_at: datetime


class PublicSaleDetailEntity(BaseModel):
    id: int
    public_sales_id: int
    private_area: float
    supply_area: float
    supply_price: int
    acquisition_tax: int
    public_sale_detail_photos: PublicSaleDetailPhotoEntity = None


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
    construct_company: Optional[str]
    supply_household: int
    is_available: bool
    offer_date: Optional[str]
    subscription_start_date: Optional[str]
    subscription_end_date: Optional[str]
    special_supply_date: Optional[str]
    special_supply_etc_date: Optional[str]
    first_supply_date: Optional[str]
    first_supply_etc_date: Optional[str]
    second_supply_date: Optional[str]
    second_supply_etc_date: Optional[str]
    notice_winner_date: Optional[str]
    contract_start_date: Optional[str]
    contract_end_date: Optional[str]
    move_in_year: int
    move_in_month: int
    min_down_payment: int
    max_down_payment: int
    down_payment_ratio: int
    reference_url: Optional[str]
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


class PrivateSaleDetailEntity(BaseModel):
    id: int
    private_sales_id: int
    private_area: float
    supply_area: float
    contract_date: Optional[str]
    deposit_price: int
    rent_price: int
    trade_price: int
    floor: int
    trade_type: Enum
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class PrivateSaleEntity(BaseModel):
    id: int
    real_estate_id: int
    building_type: Enum
    created_at: datetime
    updated_at: datetime
    private_sale_details: List[PrivateSaleDetailEntity] = None

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
    avg_trade_price: Optional[float]
    avg_deposit_price: Optional[float]
    avg_rent_price: Optional[float]
    avg_supply_price: Optional[float]
    avg_private_pyoung_number: Optional[float]
    avg_public_pyoung_number: Optional[float]
    private_sales: PrivateSaleEntity = None
    public_sales: PublicSaleEntity = None

    class Config:
        use_enum_values = True


class RealEstateWithPrivateSaleEntity(BaseModel):
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
    avg_trade_price: Optional[float]
    avg_private_pyoung_number: Optional[float]
    private_sales: PrivateSaleEntity = None

    class Config:
        use_enum_values = True


class HousePublicDetailEntity(BaseModel):
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
    is_like: bool
    min_pyoung_number: Optional[float]
    max_pyoung_number: Optional[float]
    min_supply_area: Optional[float]
    max_supply_area: Optional[float]
    avg_supply_price: Optional[float]
    supply_price_per_pyoung: Optional[float]
    min_acquisition_tax: int
    max_acquisition_tax: int
    public_sales: PublicSaleEntity = None
    near_houses: List[RealEstateWithPrivateSaleEntity] = None

    class Config:
        use_enum_values = True


class PublicSaleCalenderEntity(BaseModel):
    id: int
    real_estate_id: int
    name: str
    offer_date: Optional[str]
    subscription_start_date: Optional[str]
    subscription_end_date: Optional[str]
    special_supply_date: Optional[str]
    special_supply_etc_date: Optional[str]
    first_supply_date: Optional[str]
    first_supply_etc_date: Optional[str]
    second_supply_date: Optional[str]
    second_supply_etc_date: Optional[str]
    notice_winner_date: Optional[str]
    contract_start_date: Optional[str]
    contract_end_date: Optional[str]
    move_in_year: int
    move_in_month: int


class CalenderInfoEntity(BaseModel):
    is_like: bool
    id: int
    name: str
    road_address: str
    jibun_address: str
    public_sale: PublicSaleCalenderEntity = None


class InterestHouseListEntity(BaseModel):
    house_id: int
    type: int
    name: str
    road_address: str
    subscription_start_date: str
    subscription_end_date: str


class GetRecentViewListEntity(BaseModel):
    house_id: int
    type: int
    name: str
    image_path: Optional[str]


class GetTicketUsageResultEntity(BaseModel):
    house_id: int
    name: str
    image_path: Optional[str]


class SearchRealEstateEntity(BaseModel):
    id: int
    jibun_address: str


class SearchPublicSaleEntity(BaseModel):
    id: int
    name: str


class SearchAdministrativeDivisionEntity(BaseModel):
    id: int
    name: str


class GetSearchHouseListEntity(BaseModel):
    real_estates: List[SearchRealEstateEntity] = None
    public_sales: List[SearchPublicSaleEntity] = None
    administrative_divisions: List[SearchAdministrativeDivisionEntity] = None
