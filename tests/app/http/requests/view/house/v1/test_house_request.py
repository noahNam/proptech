import pytest

from app.http.requests.v1.house_request import GetCoordinatesRequest, GetCalenderInfoRequest
from core.domains.house.enum.house_enum import BoundingLevelEnum
from core.exceptions import InvalidRequestException

# input parameter
start_x = 126.5
start_y = 37.7
end_x = 127.09
end_y = 37.42
level = BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value


def test_get_coordinates_request_when_valid_request_then_success():
    result = GetCoordinatesRequest(
        start_x=start_x,
        start_y=start_y,
        end_x=end_x,
        end_y=end_y,
        level=level
    ).validate_request_and_make_dto()
    assert result.start_x == start_x
    assert result.start_y == start_y
    assert result.end_x == end_x
    assert result.end_y == end_y


def test_get_coordinates_request_when_invalid_coordinates_then_fail():
    wrong_start_x = 110
    with pytest.raises(InvalidRequestException):
        GetCoordinatesRequest(start_x=wrong_start_x, start_y=start_y, end_x=end_x, end_y=end_y,
                              level=level).validate_request_and_make_dto()


def test_get_coordinates_request_when_invalid_level_then_fail():
    wrong_level = 30
    with pytest.raises(InvalidRequestException):
        GetCoordinatesRequest(start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y,
                              level=wrong_level).validate_request_and_make_dto()


def test_get_calender_info_request_when_valid_value_then_success():
    year = 2021
    month = 7
    user_id = 1
    result = GetCalenderInfoRequest(year=year, month=month, user_id=user_id).validate_request_and_make_dto()

    assert result.user_id == user_id
    assert result.year == str(year)
    assert result.month == "0" + str(month)
