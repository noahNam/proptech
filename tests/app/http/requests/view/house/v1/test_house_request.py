import pytest

from app.http.requests.v1.house_request import (
    GetCoordinatesRequestSchema,
    GetCalendarInfoRequestSchema,
    GetSearchHouseListRequestSchema,
    GetBoundingWithinRadiusRequestSchema,
)
from core.domains.house.enum.house_enum import BoundingLevelEnum
from core.exceptions import InvalidRequestException

# input parameter
start_x = 126.5
start_y = 37.7
end_x = 127.09
end_y = 37.42
level = BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value


def test_get_coordinates_request_when_valid_request_then_success():
    result = GetCoordinatesRequestSchema(
        start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y, level=level
    ).validate_request_and_make_dto()
    assert result.start_x == start_x
    assert result.start_y == start_y
    assert result.end_x == end_x
    assert result.end_y == end_y


def test_get_coordinates_request_when_invalid_coordinates_then_fail():
    wrong_start_x = 110
    with pytest.raises(InvalidRequestException):
        GetCoordinatesRequestSchema(
            start_x=wrong_start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
            level=level,
        ).validate_request_and_make_dto()


def test_get_coordinates_request_when_invalid_level_then_fail():
    wrong_level = 30
    with pytest.raises(InvalidRequestException):
        GetCoordinatesRequestSchema(
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
            level=wrong_level,
        ).validate_request_and_make_dto()


def test_get_calendar_info_request_when_valid_value_then_success():
    year = 2021
    month = 7
    user_id = 1
    result = GetCalendarInfoRequestSchema(
        year=year, month=month, user_id=user_id
    ).validate_request_and_make_dto()

    assert result.user_id == user_id
    assert result.year == str(year)
    assert result.month == "0" + str(month)


def test_get_search_house_list_request_when_valid_keywords_then_success():
    keywords = "서울특별시 서초구"
    result = GetSearchHouseListRequestSchema(
        keywords=keywords
    ).validate_request_and_make_dto()

    assert result.keywords == keywords


def test_get_search_house_list_request_when_no_keywords_then_fail():
    keywords = None
    with pytest.raises(InvalidRequestException):
        GetSearchHouseListRequestSchema(
            keywords=keywords
        ).validate_request_and_make_dto()


def test_get_bounding_within_radius_request_when_valid_value_then_success():
    house_id = 1
    search_type = "2"
    result = GetBoundingWithinRadiusRequestSchema(
        house_id=house_id, search_type=search_type
    ).validate_request_and_make_dto()

    assert result.house_id == house_id
    assert result.search_type == int(search_type)


def test_get_bounding_within_radius_request_when_no_house_id_then_fail():
    house_id = None
    search_type = "2"
    with pytest.raises(InvalidRequestException):
        GetBoundingWithinRadiusRequestSchema(
            house_id=house_id, search_type=search_type
        ).validate_request_and_make_dto()


def test_get_bounding_within_radius_request_when_wrong_search_type_then_fail():
    house_id = 1
    search_type = "5"
    with pytest.raises(InvalidRequestException):
        GetBoundingWithinRadiusRequestSchema(
            house_id=house_id, search_type=search_type
        ).validate_request_and_make_dto()
