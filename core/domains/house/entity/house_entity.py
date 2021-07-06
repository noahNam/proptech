from datetime import datetime

from pydantic import BaseModel


class InterestHouseEntity(BaseModel):
    id: int
    user_id: int
    ref_id: int
    type: int
    is_like: bool
    created_at: datetime
    updated_at: datetime
