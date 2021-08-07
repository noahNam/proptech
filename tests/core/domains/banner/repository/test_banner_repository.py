from core.domains.banner.enum.banner_enum import (
    BannerSectionType,
    BannerSubTopic,
    ButtonSectionType,
)
from core.domains.banner.repository.banner_repository import BannerRepository

home_section_type = BannerSectionType.HOME_SCREEN.value
pre_subscription_section_type = BannerSectionType.PRE_SUBSCRIPTION_INFO.value


def test_when_get_banner_list_include_images_then_should_return_banner_list(
    session, banner_factory
):
    banner1 = banner_factory(
        banner_image=True,
        section_type=BannerSectionType.HOME_SCREEN.value,
        sub_topic=BannerSubTopic.HOME_THIRD_PLANNED_CITY.value,
    )
    banner2 = banner_factory(
        banner_image=True,
        section_type=BannerSectionType.HOME_SCREEN.value,
        sub_topic=BannerSubTopic.HOME_SUBSCRIPTION_BY_REGION.value,
    )

    banner3 = banner_factory(
        banner_image=True,
        section_type=BannerSectionType.HOME_SCREEN.value,
        sub_topic=BannerSubTopic.HOME_SUBSCRIPTION_GUIDE.value,
    )
    banner4 = banner_factory(
        banner_image=True,
        section_type=BannerSectionType.PRE_SUBSCRIPTION_INFO.value,
        sub_topic=BannerSubTopic.PRE_SUBSCRIPTION_FAQ.value,
    )

    session.add_all([banner1, banner2, banner3, banner4])
    session.commit()

    home_banner_list = BannerRepository().get_banner_list_include_images(
        section_type=home_section_type
    )

    pre_subscription_banner_list = BannerRepository().get_banner_list_include_images(
        section_type=pre_subscription_section_type
    )

    assert len(home_banner_list) == 3
    assert len(pre_subscription_banner_list) == 1


def test_when_get_button_link_list_then_should_return_button_link_list(
    session, button_link_factory
):
    button1 = button_link_factory(section_type=ButtonSectionType.HOME_SCREEN.value)
    button2 = button_link_factory(section_type=ButtonSectionType.HOME_SCREEN.value)
    button3 = button_link_factory(
        section_type=ButtonSectionType.PRE_SUBSCRIPTION_INFO.value
    )

    session.add_all([button1, button2, button3])
    session.commit()

    home_button_link_list = BannerRepository().get_button_link_list(
        section_type=home_section_type
    )
    pre_subscription_button_link_list = BannerRepository().get_button_link_list(
        section_type=pre_subscription_section_type
    )

    assert len(home_button_link_list) == 2
    assert len(pre_subscription_button_link_list) == 1
