from unittest.mock import patch

from flask import url_for

from core.domains.banner.enum.banner_enum import SectionType, BannerSubTopic
from core.domains.house.entity.house_entity import PublicSaleCalendarEntity, CalendarInfoEntity


def test_get_home_banner_view_when_present_date_then_return_banner_list_with_calendar_info(
        client,
        session,
        test_request_context,
        make_header,
        make_authorization,
        banner_factory
):
    # request header
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

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

    with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = [sample_calendar_info]
        with test_request_context:
            response = client.get(
                url_for("api/tanos.get_home_banner_view", section_type=SectionType.HOME_SCREEN.value),
                headers=headers,
            )

    data = response.get_json()["data"]

    assert response.status_code == 200
    assert mock_calendar_info.called is True
    assert len(data["banners"]["banner_list"]) == 2
    assert data["banners"]["calendar_infos"][0]["name"] == sample_calendar_info.name
    assert data["banners"]["calendar_infos"][0]["is_like"] == sample_calendar_info.is_like


def test_when_get_pre_subscription_banner_view_then_return_banner_list_with_button_link_list(
        client,
        session,
        test_request_context,
        make_header,
        make_authorization,
        banner_factory,
        button_link_factory,
):
    # request header
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

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

    button1 = button_link_factory(
        section_type=SectionType.PRE_SUBSCRIPTION_INFO.value
    )
    button2 = button_link_factory(
        section_type=SectionType.PRE_SUBSCRIPTION_INFO.value
    )

    session.add_all([banner1, banner2, button1, button2])
    session.commit()

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_pre_subscription_banner_view",
                    section_type=SectionType.PRE_SUBSCRIPTION_INFO.value),
            headers=headers,
        )

    data = response.get_json()["data"]
    print(data)
    assert response.status_code == 200
    assert len(data["banners"]["banner_list"]) == 2
    assert len(data["banners"]["button_links"]) == 2
