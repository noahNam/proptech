from datetime import datetime

from pydantic import BaseModel


class InterestHouseEntity(BaseModel):
    id: int
    user_id: int
    ref_id: str
    is_active: str
    created_at: datetime
    updated_at: datetime
