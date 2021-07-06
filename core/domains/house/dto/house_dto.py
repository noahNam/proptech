from pydantic import BaseModel


class InterestHouseDto(BaseModel):
    user_id: int
    ref_id: int
    type: int
    is_like: bool
