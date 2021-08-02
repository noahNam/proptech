from typing import List, Optional

from pydantic import BaseModel

from core.domains.house.entity.house_entity import GetPublicSaleOfTicketUsageEntity


class GetTicketUsageResultBaseSchema(BaseModel):
    house_id: int
    name: str
    image_path: Optional[str]


class GetTicketUsageResultResponseSchema(BaseModel):
    houses: List[GetTicketUsageResultBaseSchema]


class UseTicketResponseSchema(BaseModel):
    result: dict
