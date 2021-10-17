from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from core.domains.banner.entity.banner_entity import BannerEntity, ButtonLinkEntity
from core.domains.report.entity.report_entity import TicketUsageResultEntity


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
    path: Optional[str]
    extension: str
    created_at: datetime
    updated_at: datetime


class PublicSaleDetailEntity(BaseModel):
    id: int
    public_sales_id: int
    private_area: float
    private_pyoung_number: Optional[int]
    supply_area: float
    supply_pyoung_number: Optional[int]
    supply_price: int
    acquisition_tax: int
    area_type: str
    area_type: Optional[str]
    special_household: Optional[int]
    general_household: Optional[int]
    total_household: Optional[int]
    public_sale_detail_photos: PublicSaleDetailPhotoEntity = None


class PublicSalePhotoEntity(BaseModel):
    id: int
    public_sales_id: int
    file_name: str
    path: Optional[str]
    extension: str
    is_thumbnail: bool
    seq: int
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
    created_at: datetime
    updated_at: datetime
    public_sale_photos: List[PublicSalePhotoEntity] = None
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
    contract_ym: Optional[int]
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


class RecentlyContractedEntity(BaseModel):
    private_sales_id: int
    private_area: float
    avg_trade_price: Optional[int]
    avg_deposit_price: Optional[int]
    private_sale_avg_price_id: Optional[int]


class PrivateSaleEntity(BaseModel):
    id: int
    real_estate_id: int
    building_type: Enum
    created_at: datetime
    updated_at: datetime
    trade_status: Optional[int]
    deposit_status: Optional[int]
    private_sale_details: List[PrivateSaleDetailEntity] = None

    class Config:
        use_enum_values = True


class AdministrativeDivisionEntity(BaseModel):
    id: int
    name: str
    short_name: str
    apt_trade_price: int
    apt_deposit_price: int
    op_trade_price: int
    op_deposit_price: int
    public_sale_price: int
    level: Enum
    # coordinates: Point
    # to_entity(): coordinates 대신 아래 위경도 값 사용
    latitude: float
    longitude: float
    front_legal_code: str
    back_legal_code: str
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class RealEstateWithPrivateSaleEntity(BaseModel):
    id: int
    name: Optional[str]
    road_address: Optional[str]
    jibun_address: str
    si_do: str
    si_gun_gu: str
    dong_myun: str
    ri: Optional[str]
    road_name: Optional[str]
    road_number: Optional[str]
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
    name: Optional[str]
    road_address: Optional[str]
    jibun_address: str
    si_do: str
    si_gun_gu: str
    dong_myun: str
    ri: Optional[str]
    road_name: Optional[str]
    road_number: Optional[str]
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
    min_supply_price: Optional[int]
    max_supply_price: Optional[int]
    supply_price_per_pyoung: Optional[float]
    min_acquisition_tax: int
    max_acquisition_tax: int
    public_sales: PublicSaleEntity = None
    button_links: List[ButtonLinkEntity] = None
    ticket_usage_results: List[TicketUsageResultEntity] = None

    class Config:
        use_enum_values = True


class PublicSaleDetailCalendarEntity(BaseModel):
    id: int
    real_estate_id: int
    name: Optional[str]
    trade_type: Enum
    offer_date: Optional[str]
    subscription_start_date: Optional[str]
    subscription_end_date: Optional[str]
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

    class Config:
        use_enum_values = True


class PublicSaleSimpleCalendarEntity(BaseModel):
    id: int
    real_estate_id: int
    name: str
    trade_type: Enum
    subscription_start_date: Optional[str]
    subscription_end_date: Optional[str]
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

    class Config:
        use_enum_values = True


class DetailCalendarInfoEntity(BaseModel):
    is_like: bool
    id: int
    name: str
    road_address: str
    jibun_address: str
    public_sale: PublicSaleDetailCalendarEntity = None

    class Config:
        use_enum_values = True


class InterestHouseListEntity(BaseModel):
    house_id: int
    type: int
    name: str
    jibun_address: Optional[str]
    road_address: Optional[str]
    subscription_start_date: str
    subscription_end_date: str
    image_path: Optional[str]


class GetRecentViewListEntity(BaseModel):
    house_id: int
    type: int
    name: str
    image_path: Optional[str]


class GetSearchHouseListEntity(BaseModel):
    house_id: int
    name: str
    jibun_address: str
    is_like: bool
    image_path: Optional[str]
    subscription_start_date: Optional[str]
    subscription_end_date: Optional[str]
    status: int
    avg_down_payment: Optional[float] = 0
    avg_supply_price: Optional[float] = 0


class GetPublicSaleOfTicketUsageEntity(BaseModel):
    house_id: int
    name: str
    image_path: Optional[str]


class GetMainPreSubscriptionEntity(BaseModel):
    banner_list: List[BannerEntity] = None
    button_links: List[ButtonLinkEntity] = None


class SimpleCalendarInfoEntity(BaseModel):
    is_like: bool
    id: int
    name: str
    road_address: str
    jibun_address: str
    public_sale: PublicSaleSimpleCalendarEntity = None

    class Config:
        use_enum_values = True


class GetHouseMainEntity(BaseModel):
    banner_list: List[BannerEntity] = None
    calendar_infos: List[SimpleCalendarInfoEntity] = None


class RealEstateReportEntity(BaseModel):
    id: int
    jibun_address: Optional[str]
    si_gun_gu: Optional[str]
    latitude: float
    longitude: float


class SpecialSupplyResultReportEntity(BaseModel):
    region: Optional[str]
    region_percent: Optional[int]
    multi_children_vol: Optional[int] = 0
    newlywed_vol: Optional[int] = 0
    old_parent_vol: Optional[int] = 0
    first_life_vol: Optional[int] = 0
    total_vol: Optional[int] = 0


class GeneralSupplyResultReportEntity(BaseModel):
    region: Optional[str]
    region_percent: Optional[int]
    applicant_num: Optional[int] = 0
    competition_rate: Optional[int] = 0
    win_point: Optional[int] = 0


class PublicSaleDetailReportEntity(BaseModel):
    id: int
    public_sales_id: int
    area_type: str
    private_area: float
    supply_area: float
    supply_price: int
    acquisition_tax: int
    special_household: Optional[int]
    multi_children_house_hold: Optional[int]
    newlywed_house_hold: Optional[int]
    old_parent_house_hold: Optional[int]
    first_life_house_hold: Optional[int]
    general_household: Optional[int]
    pyoung_number: Optional[int] = 0
    price_per_meter: Optional[int] = 0
    public_sale_detail_photos: Optional[PublicSaleDetailPhotoEntity]
    special_supply_results: List[SpecialSupplyResultReportEntity] = None
    general_supply_results: List[GeneralSupplyResultReportEntity] = None


class PublicSaleReportEntity(BaseModel):
    id: int
    name: Optional[str]
    real_estate_id: int
    supply_household: int
    offer_date: Optional[str]
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
    public_sale_photo: List[PublicSalePhotoEntity]
    public_sale_details: List[PublicSaleDetailReportEntity] = None
    real_estates: RealEstateReportEntity


class PrivateSaleAvgPriceTradeEntity(BaseModel):
    pyoung: int
    trade_price: Optional[int]


class PrivateSaleAvgPriceDepositEntity(BaseModel):
    pyoung: int
    deposit_price: Optional[int]


class PrivateSaleAvgPriceEntity(BaseModel):
    trade_info: Optional[PrivateSaleAvgPriceTradeEntity]
    deposit_info: Optional[PrivateSaleAvgPriceDepositEntity]


class PublicSaleAvgPriceEntity(BaseModel):
    pyoung: int
    supply_price: Optional[int]


class PrivateSaleBoundingEntity(BaseModel):
    id: int
    building_type: Enum
    default_pyoung: Optional[int]
    trade_info: Optional[List[PrivateSaleAvgPriceTradeEntity]]
    deposit_info: Optional[List[PrivateSaleAvgPriceDepositEntity]]
    trade_status: Optional[int]
    deposit_status: Optional[int]

    class Config:
        use_enum_values = True


class PublicSaleBoundingEntity(BaseModel):
    id: int
    name: str
    default_pyoung: Optional[int]
    housing_category: Enum
    rent_type: Enum
    trade_type: Enum
    is_available: bool
    subscription_start_date: Optional[str]
    subscription_end_date: Optional[str]
    status: int
    public_sale_photos: List[PublicSalePhotoEntity]
    public_sale_avg_prices: Optional[List[PublicSaleAvgPriceEntity]]

    class Config:
        use_enum_values = True


class BoundingRealEstateEntity(BaseModel):
    id: int
    name: Optional[str]
    road_address: Optional[str]
    jibun_address: str
    si_do: str
    si_gun_gu: str
    dong_myun: str
    ri: Optional[str]
    road_name: Optional[str]
    road_number: Optional[str]
    land_number: Optional[str]
    is_available: bool
    latitude: float
    longitude: float
    private_sales: Optional[PrivateSaleBoundingEntity]
    public_sales: Optional[PublicSaleBoundingEntity]


class AdministrativeDivisionLegalCodeEntity(BaseModel):
    id: int
    name: str
    short_name: str
    front_legal_code: str
    back_legal_code: str


class RealEstateLegalCodeEntity(BaseModel):
    id: int
    jibun_address: str
    si_do: str
    si_gun_gu: str
    dong_myun: str


class PrivateSalePhotoEntity(BaseModel):
    id: int
    private_sales_id: int
    file_name: str
    path: Optional[str]
    extension: str
    is_thumbnail: bool
    seq: int
    created_at: datetime
    updated_at: datetime
