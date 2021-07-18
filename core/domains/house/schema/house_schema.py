from typing import List, Union

from pydantic import BaseModel

from core.domains.house.entity.house_entity import (
    BoundingRealEstateEntity,
    AdministrativeDivisionEntity,
    HousePublicDetailEntity,
    CalenderInfoEntity
)


class BoundingResponseSchema(BaseModel):
    houses: Union[List[BoundingRealEstateEntity], str]


class BoundingAdministrativeResponseSchema(BaseModel):
    houses: Union[List[AdministrativeDivisionEntity], str]


class GetHousePublicDetailResponseSchema(BaseModel):
    house: HousePublicDetailEntity


class GetCalenderInfoResponseSchema(BaseModel):
    houses: Union[List[CalenderInfoEntity], str]
