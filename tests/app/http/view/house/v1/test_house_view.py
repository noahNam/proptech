import json
from decimal import Decimal
from unittest.mock import patch

from flask import url_for

from app.extensions.utils.house_helper import HouseHelper
from app.extensions.utils.time_helper import get_server_timestamp
from app.http.responses import success_response
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.entity.house_entity import (
    BoundingRealEstateEntity,
    AdministrativeDivisionEntity,
    HousePublicDetailEntity,
    SimpleCalendarInfoEntity,
    PublicSaleSimpleCalendarEntity,
    PublicSaleDetailCalendarEntity,
    MainRecentPublicInfoEntity,
    DetailCalendarInfoEntity,
    MapSearchEntity,
    PublicSaleEntity,
    PublicSaleDetailEntity,
)
from core.domains.house.enum.house_enum import (
    HouseTypeEnum,
    BoundingLevelEnum,
    DivisionLevelEnum,
    SectionType,
    BannerSubTopic,
    PreSaleTypeEnum,
    BoundingPrivateTypeEnum,
    BoundingPublicTypeEnum,
    BoundingIncludePrivateEnum,
)
from core.use_case_output import UseCaseSuccessOutput

bounding_entitiy = BoundingRealEstateEntity(private_sales=None, public_sales=None,)


def test_upsert_interest_house_view_when_like_public_sales_then_insert_success(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
):
    user_id = create_users[0].id
    house_id = 1

    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(type_=HouseTypeEnum.PUBLIC_SALES.value, is_like=True)

    with test_request_context:
        response = client.post(
            url_for("api/tanos.upsert_interest_house_view", house_id=house_id),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["house"]["jibun_address"] is not None


def test_upsert_interest_house_view_when_unlike_public_sales_then_update_is_like_equals_false(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    interest_house_factory,
    create_real_estate_with_public_sale,
):
    interest_house = interest_house_factory.build()
    session.add(interest_house)

    session.commit()

    upsert_interest_house_dto = UpsertInterestHouseDto(
        user_id=1, house_id=1, type=HouseTypeEnum.PUBLIC_SALES.value, is_like=True
    )

    authorization = make_authorization(user_id=upsert_interest_house_dto.user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(type_=HouseTypeEnum.PUBLIC_SALES.value, is_like=False)

    with test_request_context:
        response = client.post(
            url_for(
                "api/tanos.upsert_interest_house_view",
                house_id=upsert_interest_house_dto.house_id,
            ),
            data=json.dumps(dict_),
            headers=headers,
        )

    filters = list()
    filters.append(InterestHouseModel.user_id == upsert_interest_house_dto.user_id)
    filters.append(InterestHouseModel.house_id == upsert_interest_house_dto.house_id)
    filters.append(InterestHouseModel.type == upsert_interest_house_dto.type)

    result = session.query(InterestHouseModel).filter(*filters).first()

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert isinstance(data["house"], dict)
    assert result.is_like is False


def test_bounding_view_when_level_is_grater_than_queryset_flag_then_success_with_bounding_presenter(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_real_estate_with_bounding,
):
    """
        geometry 함수가 사용되는 구간
        - HouseRepository().get_bounding_by_coordinates_range_dto -> mocking
        - BoundingPresenter().transform (ResponseSchema check) -> mocking
    """
    # request header
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    # input parameter
    start_x = (126.5,)
    start_y = (37.7,)
    end_x = (127.9,)
    end_y = (37.42,)
    level = BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value
    private_type = BoundingPrivateTypeEnum.APT_ONLY.value
    public_type = BoundingPublicTypeEnum.PUBLIC_ONLY.value
    include_private = BoundingIncludePrivateEnum.INCLUDE.value

    with patch(
        "app.http.responses.presenters.v1.house_presenter.BoundingPresenter.transform"
    ) as mock_result:
        mock_result.return_value = success_response(result=bounding_entitiy.dict())
        with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_bounding"
        ) as mock_get_bounding:
            mock_get_bounding.return_value = create_real_estate_with_bounding
            with test_request_context:
                response = client.get(
                    url_for(
                        "api/tanos.bounding_view",
                        start_x=start_x,
                        start_y=start_y,
                        end_x=end_x,
                        end_y=end_y,
                        level=level,
                        private_type=private_type,
                        public_type=public_type,
                        public_status=None,
                        max_area=None,
                        min_area=None,
                        include_private=include_private,
                    ),
                    headers=headers,
                )
    data = response.get_json()
    assert response.status_code == 200
    assert mock_get_bounding.called is True
    assert mock_result.called is True


def test_bounding_view_when_level_is_lower_than_queryset_flag_then_success_with_bounding_administrative_presenter(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_real_estate_with_bounding,
):
    """
        geometry 함수가 사용되는 구간
        - HouseRepository().get_administrative_by_coordinates_range_dto -> mocking
        - BoundingAdministrativePresenter().transform (ResponseSchema check) -> mocking
    """
    # request header
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    # input parameter
    start_x = (126.5,)
    start_y = (37.7,)
    end_x = (127.9,)
    end_y = (37.42,)
    level = BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value - 1
    private_type = BoundingPrivateTypeEnum.APT_ONLY.value
    public_type = BoundingPublicTypeEnum.PUBLIC_ONLY.value
    include_private = BoundingIncludePrivateEnum.INCLUDE.value

    bounding_entitiy = AdministrativeDivisionEntity(
        id=1,
        name="서울특별시 서초구",
        short_name="서초구",
        apt_trade_price=100,
        apt_deposit_price=200,
        op_trade_price=100,
        op_deposit_price=300,
        public_sale_price=400,
        level=DivisionLevelEnum.LEVEL_2,
        is_available=True,
        latitude=127,
        longitude=37.71,
        front_legal_code="11110",
        back_legal_code="10101",
        created_at=get_server_timestamp(),
        updated_at=get_server_timestamp(),
        apt_trade_visible=True,
        apt_deposit_visible=True,
        op_trade_visible=True,
        op_deposit_visible=True,
    )

    with patch(
        "app.http.responses.presenters.v1.house_presenter.BoundingAdministrativePresenter.transform"
    ) as mock_result:
        mock_result.return_value = success_response(result=bounding_entitiy.dict())
        with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_administrative_divisions"
        ) as mock_get_bounding:
            mock_get_bounding.return_value = create_real_estate_with_bounding
            with test_request_context:
                response = client.get(
                    url_for(
                        "api/tanos.bounding_view",
                        start_x=start_x,
                        start_y=start_y,
                        end_x=end_x,
                        end_y=end_y,
                        level=level,
                        private_type=private_type,
                        public_type=public_type,
                        include_private=include_private,
                    ),
                    headers=headers,
                )
    data = response.get_json()
    assert response.status_code == 200
    assert data["id"] == bounding_entitiy.id
    assert data["name"] == bounding_entitiy.name
    assert mock_get_bounding.called is True
    assert mock_result.called is True


def test_house_calendar_list_view_when_included_request_date_then_show_info_list(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_real_estate_with_public_sale,
):

    # request header
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    public_sale_detail_calendar = PublicSaleDetailCalendarEntity(
        id=1,
        real_estate_id=1,
        name="힐스테이트",
        trade_type=PreSaleTypeEnum.PRE_SALE.value,
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
        move_in_year="2023",
        move_in_month="12",
    )
    sample_calendar_info = DetailCalendarInfoEntity(
        is_like=True,
        id=1,
        road_address="서울 서초구 어딘가",
        jibun_address="서울 서초구 어딘가",
        public_sale=public_sale_detail_calendar,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_simple_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = [sample_calendar_info]
        with test_request_context:
            response = client.get(
                url_for("api/tanos.house_calendar_list_view", year=2021, month=7),
                headers=headers,
            )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert mock_calendar_info.called is True
    assert data["houses"][0]["is_like"] == sample_calendar_info.is_like


def test_house_public_detail_view_when_valid_request_id(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    real_estate_factory,
    public_sale_photo_factory,
    public_sale_factory,
):
    # request header
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    real_estate = real_estate_factory.build(public_sales=True, private_sales=False)
    public_sales = public_sale_factory.build(id=1, public_sale_details=True)

    public_sale_photo_1 = public_sale_photo_factory.build(id=1, public_sale_id=1)
    public_sale_photo_2 = public_sale_photo_factory.build(id=2, public_sale_id=1)
    # session.add(public_sale_photo_1, public_sale_photo_2)
    # session.commit()

    detail_entity = PublicSaleDetailEntity(
        id=public_sales.public_sale_details[0].id,
        public_sale_id=public_sales.public_sale_details[0].public_sale_id,
        private_area=public_sales.public_sale_details[0].private_area,
        private_pyoung_number=10,
        supply_area=public_sales.public_sale_details[0].supply_area,
        supply_pyoung_number=20,
        supply_price=public_sales.public_sale_details[0].supply_price,
        acquisition_tax=public_sales.public_sale_details[0].acquisition_tax,
        area_type="84A",
        special_household=public_sales.public_sale_details[0].special_household,
        general_household=public_sales.public_sale_details[0].general_household,
        total_household=public_sales.public_sale_details[0].total_household,
    )

    public_sales_entity = PublicSaleEntity(
        id=public_sales.id,
        real_estate_id=public_sales.real_estate_id,
        name=public_sales.name,
        region=public_sales.region,
        housing_category=public_sales.housing_category,
        rent_type=public_sales.rent_type,
        trade_type=public_sales.trade_type,
        construct_company=public_sales.construct_company,
        supply_household=public_sales.supply_household,
        is_available=public_sales.is_available,
        offer_date=public_sales.offer_date,
        offer_notice_url=public_sales.offer_notice_url,
        subscription_start_date=public_sales.subscription_start_date,
        subscription_end_date=public_sales.subscription_end_date,
        status=HouseHelper().public_status(
            offer_date=public_sales.offer_date,
            end_date=public_sales.subscription_end_date,
        ),
        special_supply_date=public_sales.special_supply_date,
        special_supply_etc_date=public_sales.special_supply_etc_date,
        special_etc_gyeonggi_date=public_sales.special_etc_gyeonggi_date,
        first_supply_date=public_sales.first_supply_date,
        first_supply_etc_date=public_sales.first_supply_etc_date,
        first_etc_gyeonggi_date=public_sales.first_etc_gyeonggi_date,
        second_supply_date=public_sales.second_supply_date,
        second_supply_etc_date=public_sales.second_supply_etc_date,
        second_etc_gyeonggi_date=public_sales.second_etc_gyeonggi_date,
        notice_winner_date=public_sales.notice_winner_date,
        contract_start_date=public_sales.contract_start_date,
        contract_end_date=public_sales.contract_end_date,
        move_in_year=public_sales.move_in_year,
        move_in_month=public_sales.move_in_month,
        min_down_payment=public_sales.min_down_payment,
        max_down_payment=public_sales.max_down_payment,
        down_payment_ratio=public_sales.down_payment_ratio,
        reference_url=public_sales.reference_url,
        created_at=public_sales.created_at,
        updated_at=public_sales.updated_at,
        is_checked=public_sales.is_checked,
        public_sale_photos=[
            public_sale_photo_1.to_entity(),
            public_sale_photo_2.to_entity(),
        ],
        public_sale_details=[detail_entity],
    )
    real_estate.public_sales = [public_sales]

    mock_query_result = [
        (
            real_estate,
            100.123,
            100.123,
            Decimal("30000.00000"),
            100.123,
            200,
            200,
            30000,
            30000,
        )
    ]

    mock_entity = HousePublicDetailEntity(
        id=1,
        name="분양아파트",
        road_address="서울특별시 서초구 어딘가1길 10",
        jibun_address="서울특별시 서초구 어딘가 123-1",
        si_do="서울특별시",
        si_gun_gu="서초구",
        dong_myun="어딘가",
        ri="-",
        road_name="어딘가1길",
        road_number="10",
        land_number="123-1",
        is_available=True,
        latitude=127,
        longitude=37.71,
        is_like=True,
        min_pyoung_number=24,
        max_pyoung_number=32,
        min_supply_area=50,
        max_supply_area=80,
        avg_supply_price=1000,
        supply_price_per_pyoung=1000,
        min_acquisition_tax=2000,
        max_acquisition_tax=3000,
        public_sales=public_sales_entity,
        is_special_supply_finished=False,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.is_enable_public_sale_house"
    ) as mock_enable:
        mock_enable.return_value = True
        with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_house_with_public_sales"
        ) as mock_house_public_detail:
            mock_house_public_detail.return_value = (
                mock_query_result,
                public_sales_entity.housing_category,
            )
            with patch(
                "core.domains.house.repository.house_repository.HouseRepository.make_house_public_detail_entity"
            ) as mock_result:
                mock_result.return_value = mock_entity
                with test_request_context:
                    response = client.get(
                        url_for("api/tanos.house_public_detail_view", house_id=1),
                        headers=headers,
                    )

    data = response.get_json()

    assert response.status_code == 200
    assert mock_house_public_detail.called is True
    assert mock_enable.called is True
    # assert data["house"]["name"] == mock_entity.name


def test_get_interest_house_list_view_when_like_one_public_sale_then_return_result_one(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
):
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_interest_house_list_view"), headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["houses"]) == 1
    assert data["houses"][0]["house_id"] == 1
    assert data["houses"][0]["type"] == HouseTypeEnum.PUBLIC_SALES.value


def test_get_interest_house_list_view_when_like_nothing_then_return_no_result(
    client, session, test_request_context, make_header, make_authorization, create_users
):
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_interest_house_list_view"), headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["houses"]) == 0


def test_get_recent_view_list_use_case_when_watch_recently_view_then_result_one(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
):
    public_sale_photo = public_sale_photo_factory.build(public_sale_id=1)
    session.add(public_sale_photo)
    session.commit()

    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_recent_view_list_view"), headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["houses"]) == 1
    assert public_sale_photo.path in data["houses"][0]["image_path"]


def test_get_search_house_list_view_when_get_no_keywords_then_fail(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
):
    """
        keywords 값 없으면 실패
    """
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_search_house_list_view", keywords=None),
            headers=headers,
        )
    assert response.status_code == 400


def test_get_search_house_list_view_when_get_less_then_1_word_keywords_then_return_null(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
):
    """
        keywords : 한글자 -> return null
    """
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_search_house_list_view", keywords="서"),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["houses"] == []


def test_get_search_house_list_view_when_get_valid_keywords_then_return_null(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
):
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    public_sale_photo = public_sale_photo_factory.build(public_sale_id=1)
    session.add(public_sale_photo)
    session.commit()

    mock_result = [
        MapSearchEntity(
            id=1,
            name="반포자이",
            latitude=37.4380785,
            longitude=126.7958879,
            house_type="분양",
        )
    ]

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_search_house_list"
    ) as mock_search:
        mock_search.return_value = mock_result
        with test_request_context:
            response = client.get(
                url_for("api/tanos.get_search_house_list_view", keywords="서울"),
                headers=headers,
            )

    data = response.get_json()["data"]

    assert response.status_code == 200
    assert mock_search.called is True
    assert data["houses"][0]["name"] == mock_result[0].name


def test_get_bounding_within_radius_view_when_no_search_type_then_fail(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
):
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_bounding_within_radius_view", house_id=1),
            headers=headers,
        )

    assert response.status_code == 400


def test_get_bounding_within_radius_view_when_wrong_search_type_then_fail(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
):
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for(
                "api/tanos.get_bounding_within_radius_view", house_id=1, search_type=4
            ),
            headers=headers,
        )

    assert response.status_code == 400


def test_get_bounding_within_radius_view_when_valid_search_type_then_success(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_bounding,
):
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    mock_output = UseCaseSuccessOutput()
    mock_output.value = create_real_estate_with_bounding

    with patch(
        "app.http.responses.presenters.v1.house_presenter.BoundingPresenter.transform"
    ) as mock_response:
        mock_response.return_value = success_response(result=bounding_entitiy.dict())

        with patch(
            "core.domains.house.use_case.v1.house_use_case"
            ".BoundingWithinRadiusUseCase.execute"
        ) as mock_result:
            mock_result.return_value = mock_output
            with test_request_context:
                response = client.get(
                    url_for(
                        "api/tanos.get_bounding_within_radius_view",
                        house_id=1,
                        search_type=1,
                    ),
                    headers=headers,
                )

    assert response.status_code == 200
    assert mock_result.called is True
    assert mock_response.called is True


def test_get_home_banner_view_when_present_date_then_return_banner_list_with_calendar_info(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    banner_factory,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
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
    public_sale_photo = public_sale_photo_factory.build(public_sale_id=1)

    session.add_all([banner1, banner2, public_sale_photo])
    session.commit()

    public_sale_simple_calendar = PublicSaleSimpleCalendarEntity(
        id=1,
        real_estate_id=1,
        name="힐스테이트",
        trade_type=PreSaleTypeEnum.PRE_SALE.value,
        subscription_start_date="20210705",
        subscription_end_date="20210705",
        special_supply_date="20210705",
        special_supply_etc_date="20210705",
        first_supply_date="20210705",
        first_supply_etc_date="20210705",
        second_supply_date="20210705",
        second_supply_etc_date="20210705",
        notice_winner_date="20210705",
    )
    sample_calendar_info = SimpleCalendarInfoEntity(
        is_like=True,
        id=1,
        road_address="서울 서초구 어딘가",
        jibun_address="서울 서초구 어딘가",
        public_sale=public_sale_simple_calendar,
    )

    sample_recent_public_info = MainRecentPublicInfoEntity(
        id=1,
        name="힐스테이트",
        si_do="서울특별시",
        status=3,
        public_sale_photo="test_photo",
        is_checked=False,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_simple_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = [sample_calendar_info]
        with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_main_recent_public_info_list"
        ) as recent_public_list:
            recent_public_list.return_value = create_real_estate_with_public_sale
            with patch(
                "core.domains.house.use_case.v1.house_use_case.GetHouseMainUseCase._make_recent_public_info_entity"
            ) as recent_public_infos:
                recent_public_infos.return_value = [sample_recent_public_info]
                with test_request_context:
                    response = client.get(
                        url_for(
                            "api/tanos.get_home_main_view",
                            section_type=SectionType.HOME_SCREEN.value,
                        ),
                        headers=headers,
                    )

    data = response.get_json()["data"]

    assert response.status_code == 200
    assert mock_calendar_info.called is True
    assert len(data["banners"]["banner_list"]) == 2
    assert (
        data["banners"]["calendar_infos"][0]["is_like"] == sample_calendar_info.is_like
    )


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

    button1 = button_link_factory(section_type=SectionType.PRE_SUBSCRIPTION_INFO.value)
    button2 = button_link_factory(section_type=SectionType.PRE_SUBSCRIPTION_INFO.value)

    session.add_all([banner1, banner2, button1, button2])
    session.commit()

    with test_request_context:
        response = client.get(
            url_for(
                "api/tanos.get_main_pre_subscription_view",
                section_type=SectionType.PRE_SUBSCRIPTION_INFO.value,
            ),
            headers=headers,
        )

    data = response.get_json()["data"]

    assert response.status_code == 200
    assert len(data["banners"]["banner_list"]) == 2
    assert len(data["banners"]["button_links"]) == 2
