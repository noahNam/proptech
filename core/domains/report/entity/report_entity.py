from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class HouseTypeRankEntity(BaseModel):
    id: int
    ticket_usage_result_id: int
    house_structure_type: str
    subscription_type: str
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
