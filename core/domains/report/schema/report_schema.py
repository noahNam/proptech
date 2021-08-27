from typing import List, Optional

from pydantic import BaseModel, StrictStr, StrictInt, StrictFloat

from core.domains.house.entity.house_entity import (
    SpecialSupplyResultReportEntity,
    GeneralSupplyResulReportEntity,
)
from core.domains.report.entity.report_entity import PredictedCompetitionEntity, SurveyResultEntity


class SortCompetitionBaseSchema(BaseModel):
    competitions: StrictInt
    house_structure_types: StrictStr
    competition_types: StrictStr


class GetExpectedCompetitionBaseSchema(BaseModel):
    nickname: StrictStr
    expected_competitions: List[PredictedCompetitionEntity]
    sort_competitions: List[SortCompetitionBaseSchema]


class GetExpectedCompetitionResponseSchema(BaseModel):
    result: GetExpectedCompetitionBaseSchema


class ReportPublicSalePhotoSchema(BaseModel):
    path: StrictStr


class ReportPublicSaleDetailPhotoSchema(BaseModel):
    path: StrictStr


class PublicSaleDetailReportSchema(BaseModel):
    area_type: StrictStr
    private_area: StrictFloat
    supply_area: StrictFloat
    supply_price: StrictInt
    special_household: StrictInt
    multi_children_house_hold: StrictInt
    newlywed_house_hold: StrictInt
    old_parent_house_hold: StrictInt
    first_life_house_hold: StrictInt
    general_household: StrictInt
    price_per_meter: StrictInt
    public_sale_detail_photo: Optional[ReportPublicSaleDetailPhotoSchema]


class RealEstateReportSchema(BaseModel):
    jibun_address: Optional[StrictStr]


class PublicSaleReportSchema(BaseModel):
    supply_household: StrictInt
    offer_date: Optional[StrictStr]
    special_supply_date: Optional[StrictStr]
    special_supply_etc_date: Optional[StrictStr]
    special_etc_gyeonggi_date: Optional[StrictStr]
    first_supply_date: Optional[StrictStr]
    first_supply_etc_date: Optional[StrictStr]
    first_etc_gyeonggi_date: Optional[StrictStr]
    second_supply_date: Optional[StrictStr]
    second_supply_etc_date: Optional[StrictStr]
    second_etc_gyeonggi_date: Optional[StrictStr]
    notice_winner_date: Optional[StrictStr]
    public_sale_photo: Optional[ReportPublicSalePhotoSchema]
    public_sale_details: List[PublicSaleDetailReportSchema] = None
    real_estates: RealEstateReportSchema


class VicinityPublicSaleReportSchema(BaseModel):
    id: StrictInt
    si_gun_gu: Optional[StrictStr]
    jibun_address: Optional[StrictStr]
    latitude: StrictFloat
    longitude: StrictFloat
    name: Optional[StrictStr]
    supply_household: StrictInt


class GetSaleInfoResponseSchema(BaseModel):
    sale_info: PublicSaleReportSchema
    recently_sale_info: VicinityPublicSaleReportSchema


class RecentlySaleDetailReportSchema(BaseModel):
    area_type: StrictStr
    private_area: StrictFloat
    supply_area: StrictFloat
    supply_price: StrictInt
    special_household: StrictInt
    general_household: StrictInt
    price_per_meter: StrictInt
    special_supply_results: List[SpecialSupplyResultReportEntity] = None
    general_supply_results: List[GeneralSupplyResulReportEntity] = None


class RecentlySaleReportSchema(BaseModel):
    supply_household: StrictInt
    offer_date: Optional[StrictStr]
    special_supply_date: Optional[StrictStr]
    special_supply_etc_date: Optional[StrictStr]
    special_etc_gyeonggi_date: Optional[StrictStr]
    first_supply_date: Optional[StrictStr]
    first_supply_etc_date: Optional[StrictStr]
    first_etc_gyeonggi_date: Optional[StrictStr]
    second_supply_date: Optional[StrictStr]
    second_supply_etc_date: Optional[StrictStr]
    second_etc_gyeonggi_date: Optional[StrictStr]
    notice_winner_date: Optional[StrictStr]
    public_sale_photo: Optional[ReportPublicSalePhotoSchema]
    public_sale_details: List[RecentlySaleDetailReportSchema] = None
    real_estates: RealEstateReportSchema


class GetRecentlySaleResponseSchema(BaseModel):
    recently_sale_info: RecentlySaleReportSchema


class GetSurveysUserReportSchema(BaseModel):
    is_ticket_usage_for_user: bool
    survey_step: int
    nickname: str
    age: Optional[int]


class GetUserSurveysResponseSchema(BaseModel):
    user: GetSurveysUserReportSchema
    survey_result: Optional[SurveyResultEntity]
