import pytest

from app.http.requests.v1.house_request import (
    GetCoordinatesRequestSchema,
    GetCalendarInfoRequestSchema,
    GetSearchHouseListRequestSchema,
    GetBoundingWithinRadiusRequestSchema,
    GetHouseMainRequestSchema,
    GetMainPreSubscriptionRequestSchema,
)
from core.domains.house.enum.house_enum import (
    BoundingLevelEnum,
    SectionType,
    BoundingPrivateTypeEnum,
    BoundingPublicTypeEnum
)
from core.exceptions import InvalidRequestException

# input parameter
start_x = 126.5
start_y = 37.7
end_x = 127.09
end_y = 37.42
level = BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value
private_type = BoundingPrivateTypeEnum.APT_ONLY.value
public_type = BoundingPublicTypeEnum.PUBLIC_ONLY.value


def test_get_coordinates_request_when_valid_request_then_success():
    result = GetCoordinatesRequestSchema(
        start_x=start_x,
        start_y=start_y,
        end_x=end_x,
        end_y=end_y,
        level=level,
        private_type=private_type,
        public_type=public_type
    ).validate_request_and_make_dto()
    assert result.start_x == start_x
    assert result.start_y == start_y
    assert result.end_x == end_x
    assert result.end_y == end_y
    assert result.private_type == private_type


def test_get_coordinates_request_when_invalid_coordinates_then_fail():
    wrong_start_x = 110
    with pytest.raises(InvalidRequestException):
        GetCoordinatesRequestSchema(
            start_x=wrong_start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
            level=level,
            private_type=private_type,
            public_type=public_type
        ).validate_request_and_make_dto()


def test_get_coordinates_request_when_invalid_private_type_then_fail():
    wrong_private_type = 5
    with pytest.raises(InvalidRequestException):
        GetCoordinatesRequestSchema(
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
            level=level,
            private_type=wrong_private_type,
            public_type=public_type
        ).validate_request_and_make_dto()


def test_get_coordinates_request_when_invalid_public_type_then_fail():
    wrong_public_type = 5
    with pytest.raises(InvalidRequestException):
        GetCoordinatesRequestSchema(
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
            level=level,
            private_type=private_type,
            public_type=wrong_public_type
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
            private_type=private_type,
            public_type=public_type
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
    user_id = "1"
    keywords = "서울특별시 서초구"
    result = GetSearchHouseListRequestSchema(
        keywords=keywords, user_id=user_id
    ).validate_request_and_make_dto()

    assert result.keywords == keywords


def test_get_search_house_list_request_when_no_keywords_then_fail():
    user_id = "1"
    keywords = None
    with pytest.raises(InvalidRequestException):
        GetSearchHouseListRequestSchema(
            keywords=keywords, user_id=user_id
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


def test_get_house_main_request_when_valid_value_then_success():
    section_type = SectionType.HOME_SCREEN.value
    user_id = 1
    result = GetHouseMainRequestSchema(
        section_type=section_type, user_id=user_id
    ).validate_request_and_make_dto()

    assert result.user_id == user_id
    assert result.section_type == section_type


def test_get_house_main_request_when_invalid_value_then_fail():
    section_type = SectionType.PRE_SUBSCRIPTION_INFO.value
    user_id = 1
    with pytest.raises(InvalidRequestException):
        GetHouseMainRequestSchema(
            section_type=section_type, user_id=user_id
        ).validate_request_and_make_dto()


def test_get_main_pre_subscription_request_when_valid_value_then_success():
    section_type = SectionType.PRE_SUBSCRIPTION_INFO.value
    result = GetMainPreSubscriptionRequestSchema(
        section_type=section_type
    ).validate_request_and_make_dto()

    assert result.section_type == section_type


def test_get_main_pre_subscription_request_when_invalid_value_then_fail():
    section_type = SectionType.HOME_SCREEN.value
    with pytest.raises(InvalidRequestException):
        GetMainPreSubscriptionRequestSchema(
            section_type=section_type
        ).validate_request_and_make_dto()
