from typing import Optional, List

from pydantic import BaseModel


class CoordinatesRangeDto(BaseModel):
    """
        위도: Y (127.xxx),
        경도: X (37.xxx)
    """

    user_id: int
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    level: int
    include_private: int
    private_type: Optional[int]
    public_type: Optional[int]
    public_status: Optional[List[int]]
    min_area: int
    max_area: int


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


class UpdateRecentViewListDto(BaseModel):
    user_id: int
    id: int
