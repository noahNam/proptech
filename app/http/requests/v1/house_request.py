from typing import Tuple

from pydantic import (
    BaseModel,
    StrictFloat,
    validator,
    ValidationError,
    StrictInt,
    StrictStr,
)

from app.extensions.utils.log_helper import logger_
from core.domains.house.dto.house_dto import (
    CoordinatesRangeDto,
    GetHousePublicDetailDto,
    GetCalendarInfoDto,
    GetSearchHouseListDto,
    BoundingWithinRadiusDto,
    SectionTypeDto,
    GetHomeBannerDto,
)
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.enum.house_enum import (
    CalendarYearThreshHold,
    SearchTypeEnum,
    SectionType,
)
from core.domains.user.dto.user_dto import GetUserDto
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class UpsertInterestHouseSchema(BaseModel):
    user_id: StrictInt
    house_id: StrictInt
    type: StrictInt
    is_like: bool


class GetInterestHouseListSchema(BaseModel):
    user_id: StrictInt


class GetRecentViewListSchema(BaseModel):
    user_id: StrictInt


class UpsertInterestHouseRequestSchema:
    def __init__(self, user_id, house_id, type_, is_like):
        self.user_id = int(user_id) if user_id else None
        self.house_id = house_id
        self.type = type_
        self.is_like = is_like

    def validate_request_and_make_dto(self):
        try:
            schema = UpsertInterestHouseSchema(
                user_id=self.user_id,
                house_id=self.house_id,
                type=self.type,
                is_like=self.is_like,
            ).dict()
            return UpsertInterestHouseDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UpsertInterestHouseRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetInterestHouseListRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetInterestHouseListSchema(user_id=self.user_id,).dict()
            return GetUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetInterestHouseListRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetRecentViewListRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetRecentViewListSchema(user_id=self.user_id,).dict()
            return GetUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetRecentViewListRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetCoordinatesSchema(BaseModel):
    """
        위도: Y (37.xxx),  <-- 주의: X Y 바뀐 형태
        경도: X (127.xxx),
        <Points>
        start(x,y)-----------
        |                   |
        |                   |
        ----------------end(x,y)
        start point 좌표가 end point 좌표보다 항상 작은 값으로 가정
        level value range: 6 ~ 21

        x_points : (start_x, end_x)
        y_points : (start_y, end_y)

        @validator
        - check_longitudes_range
        --> 두 점의 각 경도 값의 범위를 체크합니다.
            (기준: 125.0666666 - 우리나라 서해 끝 섬, 131.8722222 - 동쪽 끝 독도 사이
                and start_x 값이 end_x 값보다 작아야 합니다.)
        - check_latitudes_range
        --> 두 점의 각 위도 값의 범위를 체크합니다.
            (기준: 33.1 - 제주도 제일 아래 지역 최남단, 38.45 - 북한 제외 최북단
                and end_y 값이 start_y 값보다 작아야 합니다.)
        - check_level
        --> 네이버지도에서 지원하는 zoom_level 값의 범위를 체크합니다.
            (기준: 6 - 가장 축소했을 때 level, 21 - 가장 확대했을 때 level
    """

    x_points: Tuple[StrictFloat, StrictFloat] = ()
    y_points: Tuple[StrictFloat, StrictFloat] = ()
    level: StrictInt = None

    @validator("x_points")
    def check_longitudes_range(cls, x_points) -> Tuple:
        if not x_points or len(x_points) != 2:
            raise ValidationError(
                "x_points is None or has only one element (start_x, end_x)"
            )

        start_x = x_points[0]
        end_x = x_points[1]

        # Validation start_x
        if start_x < 125.0666666 or 131.8722222 < start_x:
            raise ValidationError("Out of range: start_longitude point (start_x)")
        elif end_x < start_x:
            raise ValidationError("Out of range: start_x should less than end_x")
        # Validation end_x
        if end_x < 125.0666666 or 131.8722222 < end_x:
            raise ValidationError("Out of range: end_longitude point (end_x)")
        elif end_x < start_x:
            raise ValidationError("Out of range: start_x should less than end_x")

        return x_points

    @validator("y_points")
    def check_latitudes_range(cls, y_points) -> Tuple:
        if not y_points or len(y_points) != 2:
            raise ValidationError(
                "x_points is None or has only one element (start_x, end_x)"
            )

        start_y = y_points[0]
        end_y = y_points[1]

        # Validation start_y
        if start_y < 33.1 or 38.45 < start_y:
            raise ValidationError("Out of range: start_latitude point (start_y)")
        elif start_y < end_y:
            raise ValidationError("Out of range: end_y should less than start_y")
        # Validation end_y
        if end_y < 33.1 or 38.45 < end_y:
            raise ValidationError("Out of range: end_latitude point (end_y)")
        elif start_y < end_y:
            raise ValidationError("Out of range: end_y should less than start_y")

        return y_points

    @validator("level")
    def check_level(cls, level) -> int:
        if level < 6 or 21 < level:
            raise ValidationError("Out of range: level value")
        return level


class GetCoordinatesRequestSchema:
    def __init__(self, start_x, start_y, end_x, end_y, level):
        self._start_x = start_x
        self._start_y = start_y
        self._end_x = end_x
        self._end_y = end_y
        self._level = level

    def validate_request_and_make_dto(self):
        try:
            schema = GetCoordinatesSchema(
                x_points=(self._start_x, self._end_x),
                y_points=(self._start_y, self._end_y),
                level=self._level,
            )

            return CoordinatesRangeDto(
                start_x=schema.x_points[0],
                start_y=schema.y_points[0],
                end_x=schema.x_points[1],
                end_y=schema.y_points[1],
                level=schema.level,
            )
        except ValidationError as e:
            logger.error(
                f"[GetCoordinatesRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetHousePublicDetailSchema(BaseModel):
    user_id: StrictInt
    house_id: StrictInt


class GetHousePublicDetailRequestSchema:
    def __init__(self, user_id, house_id):
        self.user_id = int(user_id) if user_id else None
        self.house_id = house_id

    def validate_request_and_make_dto(self):
        try:
            schema = GetHousePublicDetailSchema(
                user_id=self.user_id, house_id=self.house_id
            ).dict()
            return GetHousePublicDetailDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetHousePublicDetailRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetCalendarInfoSchema(BaseModel):
    year: str
    month: str
    user_id: StrictInt

    @validator("year")
    def check_year(cls, year) -> str:
        year_to_int = int(year)
        if (
            year_to_int < CalendarYearThreshHold.MIN_YEAR.value
            or year_to_int > CalendarYearThreshHold.MAX_YEAR.value
        ):
            raise ValidationError("Out of range: year is currently support 2017 ~ 2030")
        return year

    @validator("month")
    def check_month(cls, month) -> str:
        """
            return schema : 01, 02 ... 09, 10, 11, 12
        """
        month_to_int = int(month)
        if month_to_int < 1 or month_to_int > 12:
            raise ValidationError("Out of range: month (1 ~ 12) required")
        if 0 < month_to_int < 10:
            month = "0" + month
        return month


class GetCalendarInfoRequestSchema:
    def __init__(self, year, month, user_id):
        self.year = year
        self.month = month
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetCalendarInfoSchema(
                year=self.year, month=self.month, user_id=self.user_id
            ).dict()
            return GetCalendarInfoDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetCalendarInfoRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetSearchHouseListSchema(BaseModel):
    keywords: StrictStr = None


class GetSearchHouseListRequestSchema:
    def __init__(self, keywords):
        self.keywords = keywords

    def validate_request_and_make_dto(self):
        try:
            schema = GetSearchHouseListSchema(keywords=self.keywords).dict()
            return GetSearchHouseListDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetSearchHouseRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetBoundingWithinRadiusSchema(BaseModel):
    house_id: StrictInt
    search_type: StrictInt

    @validator("search_type")
    def check_search_type(cls, search_type) -> int:
        if (
            search_type < SearchTypeEnum.FROM_REAL_ESTATE.value
            or search_type > SearchTypeEnum.FROM_ADMINISTRATIVE_DIVISION.value
        ):
            raise ValidationError("Out of range: Available search_type - (1, 2, 3) ")
        return search_type


class GetBoundingWithinRadiusRequestSchema:
    def __init__(self, house_id, search_type):
        self.house_id = house_id
        self.search_type = int(search_type) if search_type else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetBoundingWithinRadiusSchema(
                house_id=self.house_id, search_type=self.search_type
            ).dict()
            return BoundingWithinRadiusDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetBoundingWithinRadiusRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetHouseMainSchema(BaseModel):
    section_type: int
    user_id: int

    @validator("section_type")
    def check_section_type(cls, section_type) -> str:
        if section_type != SectionType.HOME_SCREEN.value:
            raise ValidationError("Invalid section_type: need home_screen value")
        return section_type


class GetHouseMainRequestSchema:
    def __init__(self, section_type, user_id):
        self.section_type = section_type
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetHouseMainSchema(
                section_type=int(self.section_type), user_id=self.user_id
            ).dict()
            return GetHomeBannerDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetHouseMainRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetMainPreSubscriptionSchema(BaseModel):
    section_type: int

    @validator("section_type")
    def check_section_type(cls, section_type) -> str:
        if section_type != SectionType.PRE_SUBSCRIPTION_INFO.value:
            raise ValidationError("Invalid section_type: need pre_subscription value")
        return section_type


class GetMainPreSubscriptionRequestSchema:
    def __init__(self, section_type):
        self.section_type = section_type

    def validate_request_and_make_dto(self):
        try:
            schema = GetMainPreSubscriptionSchema(
                section_type=int(self.section_type)
            ).dict()
            return SectionTypeDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetMainPreSubscriptionRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
