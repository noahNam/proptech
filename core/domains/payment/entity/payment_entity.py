from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TicketTypeEntity(BaseModel):
    id: int
    division: str


class TicketTargetEntity(BaseModel):
    id: int
    ticket_id: int
    public_house_id: int


class TicketEntity(BaseModel):
    id: int
    user_id: int
    type: int
    amount: int
    sign: str
    is_active: bool
    created_by: str
    created_at: datetime
    ticket_type: Optional[TicketTypeEntity]
    ticket_targets: Optional[List[TicketTargetEntity]]


class PromotionHouseEntity(BaseModel):
    id: int
    promotion_id: int
    house_id: int


class PromotionUsageCountEntity(BaseModel):
    id: int
    promotion_id: int
    user_id: int
    usage_count: int


class PromotionEntity(BaseModel):
    id: int
    type: str
    max_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    promotion_houses: Optional[List[PromotionHouseEntity]]
    promotion_usage_count: Optional[PromotionUsageCountEntity]


class RecommendCodeEntity(BaseModel):
    id: int
    user_id: int
    code_group: int
    code: str
    code_count: int
    is_used: bool
