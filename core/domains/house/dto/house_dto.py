from typing import Optional, List

from pydantic import BaseModel


class CoordinatesRangeDto(BaseModel):
    """
        위도: Y (127.xxx),
        경도: X (37.xxx)
    """

    start_x: Optional[float]
    start_y: Optional[float]
    end_x: Optional[float]
    end_y: Optional[float]
    level: Optional[int]
    private_type: Optional[int]
    public_type: Optional[int]
    public_status: Optional[List[int]]
    min_area: Optional[int]
    max_area: Optional[int]


class UpsertInterestHouseDto(BaseModel):
    user_id: int
    house_id: int
    type: int
    is_like: bool


class GetHousePublicDetailDto(BaseModel):
    user_id: int
    house_id: int


class GetCalendarInfoDto(BaseModel):
    year: str
    month: str
    user_id: int


class GetSearchHouseListDto(BaseModel):
    keywords: str
    user_id: int


class BoundingWithinRadiusDto(BaseModel):
    house_id: int
    search_type: int


class SectionTypeDto(BaseModel):
    section_type: int


class GetHouseMainDto(BaseModel):
    section_type: int
    user_id: int


class GetHousePublicNearPrivateSalesDto(BaseModel):
    house_id: int
