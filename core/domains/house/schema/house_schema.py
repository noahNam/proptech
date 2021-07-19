from typing import List

from pydantic import BaseModel

from core.domains.house.entity.house_entity import BoundingRealEstateEntity


class BoundingResponseSchema(BaseModel):
    houses: List[BoundingRealEstateEntity]
