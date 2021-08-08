import pytest

from app.http.requests.v1.banner_request import GetHomeBannerRequestSchema, GetPreSubscriptionBannerRequestSchema
from core.domains.banner.enum.banner_enum import SectionType
from core.exceptions import InvalidRequestException


def test_get_home_banner_request_when_valid_value_then_success():
    section_type = SectionType.HOME_SCREEN.value
    user_id = 1
    result = GetHomeBannerRequestSchema(
        section_type=section_type, user_id=user_id
    ).validate_request_and_make_dto()

    assert result.user_id == user_id
    assert result.section_type == section_type


def test_get_home_banner_request_when_invalid_value_then_fail():
    section_type = SectionType.PRE_SUBSCRIPTION_INFO.value
    user_id = 1
    with pytest.raises(InvalidRequestException):
        GetHomeBannerRequestSchema(
            section_type=section_type, user_id=user_id
        ).validate_request_and_make_dto()


def test_get_pre_subscription_banner_request_when_valid_value_then_success():
    section_type = SectionType.PRE_SUBSCRIPTION_INFO.value
    result = GetPreSubscriptionBannerRequestSchema(
        section_type=section_type
    ).validate_request_and_make_dto()

    assert result.section_type == section_type


def test_get_pre_subscription_banner_request_when_invalid_value_then_fail():
    section_type = SectionType.HOME_SCREEN.value
    with pytest.raises(InvalidRequestException):
        GetPreSubscriptionBannerRequestSchema(
            section_type=section_type
        ).validate_request_and_make_dto()