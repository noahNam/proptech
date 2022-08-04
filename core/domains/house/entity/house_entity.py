from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel

from core.domains.banner.entity.banner_entity import BannerEntity, ButtonLinkEntity
from core.domains.report.entity.report_entity import (
    TicketUsageResultForHousePublicDetailEntity,
)


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
    public_sale_detail_id: int
    file_name: str
    path: Optional[str]
    extension: str
    created_at: datetime
    updated_at: datetime


class PublicSaleDetailEntity(BaseModel):
    id: int
    public_sale_id: int
    private_area: float
    private_pyoung_number: Optional[int]
    supply_area: float
    supply_pyoung_number: Optional[int]
    supply_price: int
    acquisition_tax: int
    area_type: str
    special_household: Optional[int]
    general_household: Optional[int]
    total_household: Optional[int]
    public_sale_detail_photos: Optional[str]


class PublicSalePhotoEntity(BaseModel):
    id: int
    public_sale_id: int
    file_name: str
    path: Optional[str]
    extension: str
    is_thumbnail: bool
    seq: int
    is_available: bool
    created_at: datetime
    updated_at: datetime


class PublicSaleEntity(BaseModel):
    id: int
    real_estate_id: int
    name: str
    region: str
    housing_category: str
    rent_type: str
    trade_type: str
    construct_company: Optional[str]
    supply_household: int
    offer_date: Optional[str]
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
    move_in_year: str
    move_in_month: str
    min_down_payment: int
    max_down_payment: int
    down_payment_ratio: int
    reference_url: Optional[str]
    offer_notice_url: Optional[str]
    heating_type: Optional[str]
    vl_rat: Optional[float]
    bc_rat: Optional[float]
    hhld_total_cnt: Optional[int]
    park_total_cnt: Optional[int]
    highest_floor: Optional[int]
    dong_cnt: Optional[int]
    contract_amount: Optional[int]
    middle_amount: Optional[float]
    remain_amount: Optional[float]
    sale_limit: Optional[str]
    compulsory_residence: Optional[str]
    hallway_type: Optional[str]
    is_checked: bool
    is_available: bool
    created_at: datetime
    updated_at: datetime
    public_sale_photos: Optional[List[PublicSalePhotoEntity]]
    public_sale_details: Optional[List[PublicSaleDetailEntity]]


class PublicSalePushEntity(BaseModel):
    id: int
    name: str
    region: str
    message_type: str = None


class PrivateSaleDetailEntity(BaseModel):
    id: int
    private_sale_id: int
    private_area: Optional[float]
    supply_area: Optional[float]
    contract_date: Optional[str]
    contract_ym: Optional[int]
    deposit_price: Optional[int]
    rent_price: Optional[int]
    trade_price: Optional[int]
    floor: Optional[int]
    trade_type: str
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class RecentlyContractedEntity(BaseModel):
    private_sale_id: int
    private_area: float
    supply_area: Optional[float]
    avg_trade_price: Optional[int]
    avg_deposit_price: Optional[int]
    private_sale_avg_price_id: Optional[int]
    max_trade_contract_date: Optional[str]
    max_deposit_contract_date: Optional[str]


class TypeInfoEntity(BaseModel):
    id: int
    dong_id: int
    private_area: Optional[float]
    supply_area: Optional[float]
    created_at: datetime
    updated_at: datetime


class DongInfoEntity(BaseModel):
    id: int
    private_sale_id: int
    name: Optional[str]
    hhld_cnt: Optional[int]
    grnd_flr_cnt: Optional[int]
    created_at: datetime
    updated_at: datetime
    type_infos: List[TypeInfoEntity] = None


class PrivateSaleAvgPriceTradeEntity(BaseModel):
    pyoung: float
    trade_price: Optional[int]
    max_trade_contract_date: Optional[str]
    default_trade_pyoung: Optional[float]


class PrivateSaleAvgPriceDepositEntity(BaseModel):
    pyoung: float
    deposit_price: Optional[int]
    max_deposit_contract_date: Optional[str]
    default_deposit_pyoung: Optional[float]


class PrivateSaleAvgPriceEntity(BaseModel):
    trade_info: Optional[PrivateSaleAvgPriceTradeEntity]
    deposit_info: Optional[PrivateSaleAvgPriceDepositEntity]


class HousePhotoEntity(BaseModel):
    id: int
    private_sale_id: int
    file_name: str
    path: Optional[str]
    extension: str
    is_thumbnail: bool
    seq: int
    is_available: bool
    created_at: datetime
    updated_at: datetime


class HouseTypePhotoEntity(BaseModel):
    id: int
    private_sale_id: int
    type_name: str
    file_name: str
    path: Optional[str]
    extension: str
    is_available: bool
    created_at: datetime
    updated_at: datetime


class PrivateSaleEntity(BaseModel):
    id: int
    real_estate_id: int
    name: Optional[str]
    building_type: Optional[str]
    build_year: Optional[str]
    move_in_date: Optional[str]
    dong_cnt: Optional[int]
    hhld_cnt: Optional[int]
    heat_type: Optional[str]
    hallway_type: Optional[str]
    builder: Optional[str]
    park_total_cnt: Optional[int]
    park_ground_cnt: Optional[int]
    park_underground_cnt: Optional[int]
    cctv_cnt: Optional[int]
    welfare: Optional[str]
    bc_rat: Optional[float]
    vl_rat: Optional[float]
    summer_mgmt_cost: Optional[int]
    winter_mgmt_cost: Optional[int]
    avg_mgmt_cost: Optional[int]
    public_ref_id: Optional[int]
    rebuild_ref_id: Optional[int]
    trade_status: Optional[int]
    deposit_status: Optional[int]
    is_available: bool
    created_at: datetime
    updated_at: datetime
    private_sale_details: List[PrivateSaleDetailEntity] = None
    dong_infos: List[DongInfoEntity] = None
    house_photos: List[HousePhotoEntity] = None
    house_type_photos: List[HouseTypePhotoEntity] = None
    private_sale_avg_prices: List[PrivateSaleAvgPriceEntity] = None


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
    apt_trade_visible: bool
    apt_deposit_visible: bool
    op_trade_visible: bool
    op_deposit_visible: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


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
    public_sale_id: int
    area_type: str
    private_area: float
    supply_area: float
    supply_price: int
    acquisition_tax: int
    special_household: Optional[int]
    multi_children_household: Optional[int]
    newlywed_household: Optional[int]
    old_parent_household: Optional[int]
    first_life_household: Optional[int]
    general_household: Optional[int]
    total_household: Optional[int]
    pyoung_number: Optional[int] = 0
    price_per_meter: Optional[int] = 0
    public_sale_detail_photo: Optional[str]
    special_supply_results: Optional[List[SpecialSupplyResultReportEntity]] = None
    general_supply_results: Optional[List[GeneralSupplyResultReportEntity]] = None


class RealEstateReportEntity(BaseModel):
    id: int
    jibun_address: Optional[str]
    si_do: Optional[str]
    si_gun_gu: Optional[str]
    latitude: float
    longitude: float


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
    public_sale_photos: Optional[List[PublicSalePhotoEntity]]
    public_sale_details: List[PublicSaleDetailReportEntity] = None
    real_estates: RealEstateReportEntity


class HousePublicDetailEntity(BaseModel):
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
    is_special_supply_finished: bool
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
    public_sales: Optional[PublicSaleEntity] = None
    button_links: Optional[List[ButtonLinkEntity]] = None
    ticket_usage_results: Optional[TicketUsageResultForHousePublicDetailEntity] = None
    report_recently_public_sale_info: Optional[PublicSaleReportEntity] = None

    class Config:
        use_enum_values = True


class PublicSaleDetailCalendarEntity(BaseModel):
    id: int
    real_estate_id: int
    name: Optional[str]
    trade_type: str
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
    move_in_year: str
    move_in_month: str

    class Config:
        use_enum_values = True


class PublicSaleSimpleCalendarEntity(BaseModel):
    id: int
    real_estate_id: int
    name: Optional[str]
    trade_type: str
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


class DetailCalendarInfoEntity(BaseModel):
    is_like: bool
    id: int
    road_address: Optional[str]
    jibun_address: Optional[str]
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
    id: int
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
    road_address: Optional[str]
    jibun_address: Optional[str]
    public_sale: PublicSaleSimpleCalendarEntity = None

    class Config:
        use_enum_values = True


class MainRecentPublicInfoEntity(BaseModel):
    id: int
    name: Optional[str]
    si_do: Optional[str]
    status: int
    public_sale_photo: Optional[str]
    is_checked: bool


class GetHouseMainEntity(BaseModel):
    banner_list: List[BannerEntity] = None
    calendar_infos: List[SimpleCalendarInfoEntity] = None
    recent_public_infos: List[MainRecentPublicInfoEntity] = None


class PublicSaleAvgPriceEntity(BaseModel):
    pyoung: int
    supply_price: Optional[int]
    avg_competition: Optional[int]
    min_score: Optional[int]


class PrivateSaleBoundingEntity(BaseModel):
    real_estate_id: int
    jibun_address: Optional[str]
    road_address: Optional[str]
    latitude: float
    longitude: float
    private_sale_id: int
    building_type: str
    name: Optional[str]
    trade_status: Optional[int]
    deposit_status: Optional[int]
    trade_pyoung: Optional[int]
    trade_price: Optional[int]
    deposit_pyoung: Optional[int]
    deposit_price: Optional[int]

    class Config:
        use_enum_values = True


class PublicSaleBoundingEntity(BaseModel):
    real_estate_id: str
    jibun_address: Optional[str]
    road_address: Optional[str]
    latitude: float
    longitude: float
    public_sale_id: int
    housing_category: str
    name: Optional[str]
    status: int
    pyoung: Optional[int]
    supply_price: int
    avg_competition: Optional[str]
    min_score: Optional[str]

    class Config:
        use_enum_values = True


class BoundingRealEstateEntity(BaseModel):
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


class MapSearchEntity(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    house_type: str


class NearHouseEntity(BaseModel):
    real_estate_id: int
    jibun_address: Optional[str]
    road_address: Optional[str]
    latitude: float
    longitude: float
    private_sale_id: int
    building_type: str
    name: Optional[str]
    trade_pyoung: Optional[int]
    trade_price: Optional[int]
    trade_status: Optional[int]

    class Config:
        use_enum_values = True


class UpdateContractStatusTargetEntity(BaseModel):
    private_sale_id: int
    min_contract_date: Optional[str]
    max_contract_date: Optional[str]
    trade_type: Enum

    class Config:
        use_enum_values = True


class CheckIdsRealEstateEntity(BaseModel):
    """
        기존에 이미 매매건으로 전환된 private_sales 에 대하여 업데이트 하기 위한 엔티티
    """

    real_estate_id: int
    public_sale_id: int
    private_sale_id: int
    supply_household: Optional[int]
    move_in_year: Optional[str]
    construct_company: Optional[str]


class SyncFailureHistoryEntity(BaseModel):
    id: Optional[int]
    target_table: Optional[str]
    sync_data: Optional[Dict]
    is_solved: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
class AddSupplyAreaEntity(BaseModel):
    req_front_legal_code: Optional[str]
    req_back_legal_code: Optional[str]
    req_land_number: Optional[str]
    req_real_estate_id: Optional[int]
    req_real_estate_name: Optional[str]
    req_private_sale_id: Optional[int]
    req_private_sale_name: Optional[str]
    req_private_building_type: Enum
    req_jibun_address: Optional[str]
    req_road_address: Optional[str]
    resp_rnum: Optional[int]
    resp_total_count: Optional[int]
    resp_name: Optional[str]
    resp_dong_nm: Optional[str]
    resp_ho_nm: Optional[str]
    resp_flr_no_nm: Optional[str]
    resp_area: Optional[float]
    resp_jibun_address: Optional[str]
    resp_road_address: Optional[str]
    resp_expos_pubuse_gb_cd_nm: Optional[str]
    resp_main_atch_gb_cd: Optional[int]
    resp_main_atch_gb_cd_nm: Optional[str]
    resp_main_purps_cd: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        use_enum_values = True


# todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
class BindTargetSupplyAreaEntity(BaseModel):
    real_estate_name: Optional[str]
    private_sale_name: Optional[str]
    real_estate_id: Optional[int]
    private_sale_id: Optional[int]
    private_area: Optional[float]
    supply_area: Optional[float]
    front_legal_code: Optional[str]
    back_legal_code: Optional[str]
    jibun_address: Optional[str]
    road_address: Optional[str]
    land_number: Optional[str]
    ref_summary_id: Optional[int]


# todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
class BindSuccessSupplyAreaEntity(BaseModel):
    real_estate_name: Optional[str]
    private_sale_name: Optional[str]
    real_estate_id: Optional[int]
    private_sale_id: Optional[int]
    private_area: Optional[float]
    supply_area: Optional[float]
    front_legal_code: Optional[str]
    back_legal_code: Optional[str]
    jibun_address: Optional[str]
    road_address: Optional[str]
    land_number: Optional[str]
    ref_summary_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
class BindFailureSupplyAreaEntity(BaseModel):
    real_estate_name: Optional[str]
    private_sale_name: Optional[str]
    real_estate_id: Optional[int]
    private_sale_id: Optional[int]
    private_area: Optional[float]
    supply_area: Optional[float]
    front_legal_code: Optional[str]
    back_legal_code: Optional[str]
    jibun_address: Optional[str]
    road_address: Optional[str]
    land_number: Optional[str]
    failure_reason: Optional[str]
    is_done: Optional[bool]
    ref_summary_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
