from typing import Tuple

from pydantic import BaseModel, StrictFloat, validator, ValidationError, StrictInt

from app.extensions.utils.log_helper import logger_
from core.domains.house.dto.house_dto import CoordinatesRangeDto, GetHousePublicDetailDto
from pydantic import BaseModel, StrictInt, ValidationError
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class UpsertInterestHouseSchema(BaseModel):
    user_id: StrictInt
    house_id: StrictInt
    type: StrictInt
    is_like: bool


class UpsertInterestHouseRequestSchema:
    def __init__(
            self, user_id, house_id, type_, is_like
    ):
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


class GetCoordinatesRequestSchema(BaseModel):
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
    def check_longitudes_range(cls, x_points):
        if not x_points or len(x_points) != 2:
            raise ValidationError("x_points is None or has only one element (start_x, end_x)")

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
    def check_latitudes_range(cls, y_points):
        if not y_points or len(y_points) != 2:
            raise ValidationError("x_points is None or has only one element (start_x, end_x)")

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
    def check_level(cls, level):
        if level < 6 or 21 < level:
            raise ValidationError("Out of range: level value")
        return level


class GetCoordinatesRequest:
    def __init__(self, start_x, start_y, end_x, end_y, level):
        self._start_x = start_x
        self._start_y = start_y
        self._end_x = end_x
        self._end_y = end_y
        self._level = level

    def validate_request_and_make_dto(self):
        try:
            schema = GetCoordinatesRequestSchema(
                x_points=(self._start_x, self._end_x),
                y_points=(self._start_y, self._end_y),
                level=self._level
            )

            return CoordinatesRangeDto(start_x=schema.x_points[0],
                                       start_y=schema.y_points[0],
                                       end_x=schema.x_points[1],
                                       end_y=schema.y_points[1],
                                       level=schema.level)
        except ValidationError as e:
            logger.error(
                f"[GetCoordinatesRequestSchema][validate_request_and_make_dto] error : {e}")


class GetHousePublicDetailRequestSchema(BaseModel):
    user_id: StrictInt
    house_id: StrictInt


class GetHousePublicDetailRequest:
    def __init__(self, user_id, house_id):
        self.user_id = int(user_id) if user_id else None
        self.house_id = house_id

    def validate_request_and_make_dto(self):
        try:
            schema = GetHousePublicDetailRequestSchema(
                user_id=self.user_id,
                house_id=self.house_id).dict()
            return GetHousePublicDetailDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetHousePublicDetailRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
