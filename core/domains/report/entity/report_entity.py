from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class HouseTypeRankEntity(BaseModel):
    id: int
    ticket_usage_result_id: int
    house_type: str
    subscription_type: str
    rank: int


class TicketUsageResultEntity(BaseModel):
    id: int
    user_id: int
    public_house_id: Optional[int]
    ticket_id: Optional[int]
    is_active: bool
    created_at: datetime
    house_type_ranks: List[HouseTypeRankEntity]
