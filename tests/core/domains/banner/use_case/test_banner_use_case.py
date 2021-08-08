from unittest.mock import patch

from core.domains.banner.dto.banner_dto import GetHomeBannerDto, SectionTypeDto
from core.domains.banner.entity.banner_entity import (
    GetHomeBannerEntity,
    GetPreSubscriptionBannerEntity,
)
from core.domains.banner.enum.banner_enum import SectionType, BannerSubTopic
from core.domains.banner.use_case.v1.banner_use_case import (
    GetHomeBannerUseCase,
    GetPreSubscriptionBannerUseCase,
)
from core.domains.house.entity.house_entity import (
    PublicSaleCalendarEntity,
    CalendarInfoEntity,
)
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput


def test_when_get_home_banner_use_case_then_include_present_calendar_info_by_pubsub(
    session, create_users, banner_factory
):
    """
        get_calendar_info_by_get_calendar_info_dto -> return mocking
    """
    banner1 = banner_factory(
        banner_image=True,
        section_type=SectionType.HOME_SCREEN.value,
        sub_topic=BannerSubTopic.HOME_THIRD_PLANNED_CITY.value,
    )
    banner2 = banner_factory(
        banner_image=True,
        section_type=SectionType.HOME_SCREEN.value,
        sub_topic=BannerSubTopic.HOME_SUBSCRIPTION_BY_REGION.value,
    )

    session.add_all([banner1, banner2])
    session.commit()

    public_sale_calendar = PublicSaleCalendarEntity(
        id=1,
        real_estate_id=1,
        name="힐스테이트",
        offer_date="20210705",
        subscription_start_date="20210705",
        subscription_end_date="20210705",
        special_supply_date="20210705",
        special_supply_etc_date="20210705",
        first_supply_date="20210705",
        first_supply_etc_date="20210705",
        second_supply_date="20210705",
        second_supply_etc_date="20210705",
        notice_winner_date="20210705",
        contract_start_date="20210705",
        contract_end_date="20210705",
        move_in_year=2023,
        move_in_month=12,
    )
    sample_calendar_info = CalendarInfoEntity(
        is_like=True,
        id=1,
        name="힐스테이트",
        road_address="서울 서초구 어딘가",
        jibun_address="서울 서초구 어딘가",
        public_sale=public_sale_calendar,
    )

    dto = GetHomeBannerDto(
        section_type=SectionType.HOME_SCREEN.value, user_id=create_users[0].id
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = [sample_calendar_info]
        result = GetHomeBannerUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, GetHomeBannerEntity)
    assert mock_calendar_info.called is True


def test_when_get_home_banner_use_case_with_wrong_section_type_then_fail(
    session, create_users
):
    invalid_dto = GetHomeBannerDto(
        section_type=SectionType.PRE_SUBSCRIPTION_INFO.value, user_id=create_users[0].id
    )
    result = GetHomeBannerUseCase().execute(dto=invalid_dto)

    assert isinstance(result, UseCaseFailureOutput)


def test_when_get_pre_subscription_banner_use_case_then_return_pre_subscription_banner_info_with_button_links(
    session, create_users, button_link_factory, banner_factory
):
    banner1 = banner_factory(
        banner_image=True,
        section_type=SectionType.PRE_SUBSCRIPTION_INFO.value,
        sub_topic=BannerSubTopic.PRE_SUBSCRIPTION_FAQ.value,
    )
    banner2 = banner_factory(
        banner_image=True,
        section_type=SectionType.PRE_SUBSCRIPTION_INFO.value,
        sub_topic=BannerSubTopic.PRE_SUBSCRIPTION_FAQ.value,
    )

    button1 = button_link_factory(section_type=SectionType.PRE_SUBSCRIPTION_INFO.value)
    button2 = button_link_factory(section_type=SectionType.PRE_SUBSCRIPTION_INFO.value)

    session.add_all([banner1, banner2, button1, button2])
    session.commit()

    dto = SectionTypeDto(section_type=SectionType.PRE_SUBSCRIPTION_INFO.value)

    result = GetPreSubscriptionBannerUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, GetPreSubscriptionBannerEntity)


def test_when_get_pre_subscription_banner_use_case_with_wrong_section_type_then_fail(
    session,
):
    invalid_dto = SectionTypeDto(section_type=SectionType.HOME_SCREEN.value)
    result = GetPreSubscriptionBannerUseCase().execute(dto=invalid_dto)

    assert isinstance(result, UseCaseFailureOutput)
