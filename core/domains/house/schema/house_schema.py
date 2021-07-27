from typing import List, Union

from pydantic import BaseModel, StrictStr

from core.domains.house.entity.house_entity import (
    BoundingRealEstateEntity,
    AdministrativeDivisionEntity,
    HousePublicDetailEntity,
    CalenderInfoEntity,
)


class GetInterestHouseListBaseSchema(BaseModel):
    house_id: int
    type: int
    name: str
    road_address: str
    subscription_start_date: str
    subscription_end_date: str


class GetRecentViewListBaseSchema(BaseModel):
    house_id: int
    type: int
    name: str
    image_path: str


class BoundingResponseSchema(BaseModel):
    houses: Union[List[BoundingRealEstateEntity], str]


class BoundingAdministrativeResponseSchema(BaseModel):
    houses: Union[List[AdministrativeDivisionEntity], str]


class GetHousePublicDetailResponseSchema(BaseModel):
    house: HousePublicDetailEntity


class GetCalenderInfoResponseSchema(BaseModel):
    houses: Union[List[CalenderInfoEntity], str]


class UpsertInterestHouseResponseSchema(BaseModel):
    result: StrictStr


class GetInterestHouseListResponseSchema(BaseModel):
    houses: List[GetInterestHouseListBaseSchema]


class GetRecentViewListResponseSchema(BaseModel):
    houses: List[GetRecentViewListBaseSchema]


class GetSearchHouseListResponseSchema(BaseModel):
    houses: Union[List[BoundingRealEstateEntity], str]


class BoundingWithinRadiusResponseSchema(BaseModel):
    houses: Union[List[BoundingRealEstateEntity], str]
