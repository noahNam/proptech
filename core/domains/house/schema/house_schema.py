from typing import List, Union, Optional

from pydantic import BaseModel

from core.domains.house.entity.house_entity import (
    BoundingRealEstateEntity,
    AdministrativeDivisionEntity,
    HousePublicDetailEntity,
    GetSearchHouseListEntity,
    GetHouseMainEntity,
    GetMainPreSubscriptionEntity,
    SimpleCalendarInfoEntity,
    RealEstateWithPrivateSaleEntity,
)


class GetInterestHouseListBaseSchema(BaseModel):
    house_id: int
    type: int
    name: str
    jibun_address: str
    subscription_start_date: str
    subscription_end_date: str
    image_path: Optional[str]


class GetRecentViewListBaseSchema(BaseModel):
    house_id: int
    type: int
    name: str
    image_path: str


class BoundingResponseSchema(BaseModel):
    houses: Optional[List[BoundingRealEstateEntity]]


class BoundingAdministrativeResponseSchema(BaseModel):
    houses: Union[Optional[List[AdministrativeDivisionEntity]], str]


class GetHousePublicDetailResponseSchema(BaseModel):
    house: Optional[HousePublicDetailEntity]


class GetCalendarInfoResponseSchema(BaseModel):
    houses: List[SimpleCalendarInfoEntity]


class UpsertInterestHouseResponseSchema(BaseModel):
    house: GetInterestHouseListBaseSchema


class GetInterestHouseListResponseSchema(BaseModel):
    houses: List[GetInterestHouseListBaseSchema]


class GetRecentViewListResponseSchema(BaseModel):
    houses: List[GetRecentViewListBaseSchema]


class GetSearchHouseListResponseSchema(BaseModel):
    houses: Optional[GetSearchHouseListEntity]


class GetHouseMainResponseSchema(BaseModel):
    banners: Optional[GetHouseMainEntity]


class GetMainPreSubscriptionResponseSchema(BaseModel):
    banners: Optional[GetMainPreSubscriptionEntity]


class GetHousePublicPrivateSalesResponseSchema(BaseModel):
    near_houses: Optional[List[RealEstateWithPrivateSaleEntity]]
