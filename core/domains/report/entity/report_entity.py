from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class HouseTypeRankEntity(BaseModel):
    id: int
    ticket_usage_result_id: int
    house_structure_type: str
    subscription_type: str
    competition: int
    rank: int


class PredictedCompetitionEntity(BaseModel):
    id: int
    ticket_usage_result_id: int
    house_structure_type: str
    region: str
    region_percentage: int
    multiple_children_competition: Optional[int]
    newly_marry_competition: Optional[int]
    old_parent_competition: Optional[int]
    first_life_competition: Optional[int]
    multiple_children_supply: Optional[int]
    newly_marry_supply: Optional[int]
    old_parent_supply: Optional[int]
    first_life_supply: Optional[int]
    normal_competition: Optional[int]
    normal_supply: Optional[int]
    normal_passing_score: Optional[int]
    total_special_supply: Optional[int]
    total_normal_supply: Optional[int]


class UserAnalysisEntity(BaseModel):
    id: int
    ticket_usage_result_id: int
    div: str
    category: int
    created_at: datetime


class TicketUsageResultEntity(BaseModel):
    id: int
    user_id: int
    type: str
    public_house_id: Optional[int]
    ticket_id: Optional[int]
    is_active: bool
    created_at: datetime
    house_type_ranks: List[HouseTypeRankEntity]
    user_analysis: List[UserAnalysisEntity]
    predicted_competitions: List[PredictedCompetitionEntity]


class TicketUsageResultUserReportEntity(BaseModel):
    id: int
    user_id: int
    type: str
    public_house_id: Optional[int]
    ticket_id: Optional[int]
    is_active: bool
    created_at: datetime
    user_analysis: List[UserAnalysisEntity]


class SurveyResultEntity(BaseModel):
    id = int
    user_id = int
    total_point: Optional[int]
    detail_point_house: Optional[int]
    detail_point_family: Optional[int]
    detail_point_bank: Optional[int]
    public_newly_married: Optional[int]
    public_married_income_point: Optional[int]
    public_married_child_point: Optional[int]
    public_married_address_point: Optional[int]
    public_married_bank_point: Optional[int]
    public_married_date_point: Optional[int]
    private_married_child_num: Optional[int]
    private_married_rank: Optional[int]
    public_newly_married_div: Optional[str]
    public_first_life: Optional[bool]
    public_first_life_div: Optional[str]
    public_multiple_children: Optional[int]
    public_old_parent: Optional[int]
    public_agency_recommend: Optional[int]
    public_normal: Optional[int]
    private_newly_married: Optional[int]
    private_newly_married_div: Optional[str]
    private_first_life: Optional[bool]
    private_first_life_div: Optional[str]
    private_multiple_children: Optional[int]
    private_old_parent: Optional[int]
    private_agency_recommend: Optional[int]
    private_normal: Optional[int]
    hope_town_phase_one: Optional[int]
    hope_town_phase_two: Optional[int]
    hope_one_income_point: Optional[int]
    hope_one_address_point: Optional[int]
    hope_one_bank_point: Optional[int]
    hope_two_child_point: Optional[int]
    hope_two_household_point: Optional[int]
    hope_two_address_point: Optional[int]
    hope_two_bank_point: Optional[int]
    created_at = datetime
    updated_at = datetime


class UserAnalysisCategoryDetailEntity(BaseModel):
    id: int
    user_analysis_category_id: int
    format_text: str


class UserAnalysisCategoryEntity(BaseModel):
    id: int
    div: str
    category: int
    title: str
    output_text: str
    user_analysis_category_detail: Optional[UserAnalysisCategoryDetailEntity]
    seq: int
    type: str
    is_active: bool
