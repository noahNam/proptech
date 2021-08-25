from typing import List, Optional

from pydantic import BaseModel, StrictStr, StrictInt, StrictFloat

from core.domains.house.entity.house_entity import PublicSaleReportEntity
from core.domains.report.entity.report_entity import PredictedCompetitionEntity


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
    price_per_meter: StrictInt
    public_sale_detail_photo: Optional[ReportPublicSaleDetailPhotoSchema]
    special_supply_results: Optional[List[ReportPublicSaleDetailPhotoSchema]]
    general_supply_results: Optional[List[ReportPublicSaleDetailPhotoSchema]]


class PublicSaleReportSchema(BaseModel):
    id: int
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
    public_sale_photo: Optional[ReportPublicSalePhotoSchema]
    public_sale_details: List[PublicSaleDetailReportSchema] = None


class GetSaleInfoBaseSchema(BaseModel):
    sale_infos: List[PublicSaleReportSchema]


class GetSaleInfoResponseSchema(BaseModel):
    result: GetSaleInfoBaseSchema
