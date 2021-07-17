from typing import List

from pydantic import BaseModel

from core.domains.house.entity.house_entity import (
    BoundingRealEstateEntity,
    AdministrativeDivisionEntity,
    HousePublicDetailEntity
)


class BoundingResponseSchema(BaseModel):
    houses: List[BoundingRealEstateEntity]


class BoundingAdministrativeResponseSchema(BaseModel):
    houses: List[AdministrativeDivisionEntity]


class GetHousePublicDetailResponseSchema(BaseModel):
    house: HousePublicDetailEntity
