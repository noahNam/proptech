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


class TicketUsageResultDetailEntity(BaseModel):
    id: int
    ticket_usage_result_id: int
    house_type: str
    subscription_type: str
    rank: int


class TicketUsageResultEntity(BaseModel):
    id: int
    user_id: int
    house_id: int
    ticket_id: int
    is_active: bool
    created_at: datetime
    ticket_usage_result_details: TicketUsageResultDetailEntity


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
    max_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    promotion_houses: List[PromotionHouseEntity]
    promotion_usage_count: PromotionUsageCountEntity
