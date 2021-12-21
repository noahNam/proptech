from datetime import datetime
from enum import Enum
from typing import List, Union, Optional, Dict

from pydantic import BaseModel, StrictStr

from core.domains.banner.entity.banner_entity import ButtonLinkEntity
from core.domains.house.entity.house_entity import (
    BoundingRealEstateEntity,
    AdministrativeDivisionEntity,
    HousePublicDetailEntity,
    GetHouseMainEntity,
    GetMainPreSubscriptionEntity,
    SimpleCalendarInfoEntity,
    MapSearchEntity,
    NearHouseEntity,
    PublicSaleReportEntity,
)
from core.domains.report.entity.report_entity import (
    TicketUsageResultForHousePublicDetailEntity,
)


class GetInterestHouseListBaseSchema(BaseModel):
    house_id: int
    type: int
    name: str
    jibun_address: Optional[str]
    road_address: Optional[str]
    subscription_start_date: str
    subscription_end_date: str
    image_path: Optional[str]


class GetRecentViewListBaseSchema(BaseModel):
    id: int
    house_id: int
    type: int
    name: str
    image_path: Optional[str]


class BoundingResponseSchema(BaseModel):
    houses: List[BoundingRealEstateEntity]


class BoundingAdministrativeResponseSchema(BaseModel):
    houses: Union[Optional[List[AdministrativeDivisionEntity]], str]


class PublicSaleDetailBaseSchema(BaseModel):
    id: int
    real_estate_id: int
    name: str
    region: str
    housing_category: str
    rent_type: Enum
    trade_type: Enum
    construct_company: Optional[str]
    supply_household: int
    is_available: bool
    offer_date: Optional[str]
    offer_notice_url: Optional[str]
    subscription_start_date: Optional[str]
    subscription_end_date: Optional[str]
    status: int
    special_supply_date: Optional[str]
    special_supply_etc_date: Optional[str]
    special_etc_gyeonggi_date: Optional[str]
    first_supply_date: Optional[str]
    first_supply_etc_date: Optional[str]
    first_etc_gyeonggi_date: Optional[str]
    second_supply_date: Optional[str]
    second_supply_etc_date: Optional[str]
    second_etc_gyeonggi_date: Optional[str]
    notice_winner_date: Optional[str]
    contract_start_date: Optional[str]
    contract_end_date: Optional[str]
    move_in_year: int
    move_in_month: int
    min_down_payment: int
    max_down_payment: int
    down_payment_ratio: int
    reference_url: Optional[str]
    total_household: Optional[int]
    total_park_number: Optional[int]
    top_floor: Optional[int]
    dong_number: Optional[int]
    contract_amount: Optional[int]
    middle_amount: Optional[float]
    remain_amount: Optional[float]
    sale_limit: Optional[str]
    public_sale_details: Optional[Dict]

    class Config:
        use_enum_values = True


class HousePublicDetailSchema(BaseModel):
    id: int
    name: Optional[str]
    road_address: Optional[str]
    jibun_address: Optional[str]
    si_do: Optional[str]
    si_gun_gu: Optional[str]
    dong_myun: Optional[str]
    ri: Optional[str]
    road_name: Optional[str]
    road_number: Optional[str]
    land_number: Optional[str]
    is_available: bool
    latitude: float
    longitude: float
    is_like: bool
    min_pyoung_number: Optional[float]
    max_pyoung_number: Optional[float]
    min_supply_area: Optional[float]
    max_supply_area: Optional[float]
    avg_supply_price: Optional[float]
    min_supply_price: Optional[int]
    max_supply_price: Optional[int]
    supply_price_per_pyoung: Optional[float]
    min_acquisition_tax: Optional[int]
    max_acquisition_tax: Optional[int]
    public_sales: Optional[PublicSaleDetailBaseSchema]
    public_sale_photos: Optional[List[str]]
    button_links: Optional[List[ButtonLinkEntity]]
    ticket_usage_results: Optional[TicketUsageResultForHousePublicDetailEntity]
    house_applicants: Optional[Dict]

    class Config:
        use_enum_values = True


class GetHousePublicDetailResponseSchema(BaseModel):
    house: Optional[HousePublicDetailSchema]


class GetCalendarInfoResponseSchema(BaseModel):
    houses: List[SimpleCalendarInfoEntity]


class UpsertInterestHouseResponseSchema(BaseModel):
    house: GetInterestHouseListBaseSchema


class GetInterestHouseListResponseSchema(BaseModel):
    houses: List[GetInterestHouseListBaseSchema]


class GetRecentViewListResponseSchema(BaseModel):
    houses: List[GetRecentViewListBaseSchema]


class GetSearchHouseListResponseSchema(BaseModel):
    houses: List[MapSearchEntity]


class GetHouseMainResponseSchema(BaseModel):
    banners: Optional[GetHouseMainEntity]


class GetMainPreSubscriptionResponseSchema(BaseModel):
    banners: Optional[GetMainPreSubscriptionEntity]


class GetHousePublicPrivateSalesResponseSchema(BaseModel):
    near_houses: Optional[List[NearHouseEntity]]


class UpdateRecentViewListResponseSchema(BaseModel):
    result: StrictStr
