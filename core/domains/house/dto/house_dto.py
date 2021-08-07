from pydantic import BaseModel


class CoordinatesRangeDto(BaseModel):
    """
        위도: Y (127.xxx),
        경도: X (37.xxx)
    """

    start_x: float
    start_y: float
    end_x: float
    end_y: float
    level: int


class UpsertInterestHouseDto(BaseModel):
    user_id: int
    house_id: int
    type: int
    is_like: bool


class GetHousePublicDetailDto(BaseModel):
    user_id: int
    house_id: int


class GetcalendarInfoDto(BaseModel):
    year: str
    month: str
    user_id: int


class GetSearchHouseListDto(BaseModel):
    keywords: str


class BoundingWithinRadiusDto(BaseModel):
    house_id: int
    search_type: int
