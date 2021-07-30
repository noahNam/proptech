import json
from unittest.mock import patch

from flask import url_for

from app.extensions.utils.time_helper import get_server_timestamp
from app.http.responses import success_response
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.entity.house_entity import (
    BoundingRealEstateEntity,
    AdministrativeDivisionEntity,
    CalenderInfoEntity,
    PublicSaleCalenderEntity,
    HousePublicDetailEntity,
)
from core.domains.house.enum.house_enum import (
    HouseTypeEnum,
    BoundingLevelEnum,
    DivisionLevelEnum,
)


def test_upsert_interest_house_view_when_like_public_sales_then_insert_success(
    client, session, test_request_context, make_header, make_authorization, create_users
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
    assert data["result"] == "success"


def test_upsert_interest_house_view_when_unlike_public_sales_then_update_is_like_equals_false(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    interest_house_factory,
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
    assert data["result"] == "success"
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

    bounding_entitiy = BoundingRealEstateEntity(
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
        avg_trade_price=100,
        avg_deposit_price=200,
        avg_rent_price=50,
        avg_supply_price=300,
        avg_private_pyoung_number=10,
        avg_public_pyoung_number=20,
        private_sales=None,
        public_sales=None,
    )

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
                    ),
                    headers=headers,
                )
    data = response.get_json()
    assert response.status_code == 200
    assert data["id"] == bounding_entitiy.id
    assert data["name"] == bounding_entitiy.name
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

    bounding_entitiy = AdministrativeDivisionEntity(
        id=1,
        name="서울특별시 서초구",
        short_name="서초구",
        real_trade_price=100,
        real_rent_price=200,
        real_deposit_price=300,
        public_sale_price=400,
        level=DivisionLevelEnum.LEVEL_2,
        is_available=True,
        latitude=127,
        longitude=37.71,
        created_at=get_server_timestamp(),
        updated_at=get_server_timestamp(),
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
                    ),
                    headers=headers,
                )
    data = response.get_json()
    assert response.status_code == 200
    assert data["id"] == bounding_entitiy.id
    assert data["name"] == bounding_entitiy.name
    assert mock_get_bounding.called is True
    assert mock_result.called is True


def test_house_calender_list_view_when_included_request_date_then_show_info_list(
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

    public_sale_calender = PublicSaleCalenderEntity(
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
    sample_calender_info = CalenderInfoEntity(
        is_like=True,
        id=1,
        name="힐스테이트",
        road_address="서울 서초구 어딘가",
        jibun_address="서울 서초구 어딘가",
        public_sale=public_sale_calender,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_calender_info"
    ) as mock_calender_info:
        mock_calender_info.return_value = [sample_calender_info]
        with test_request_context:
            response = client.get(
                url_for("api/tanos.house_calender_list_view", year=2021, month=7),
                headers=headers,
            )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert mock_calender_info.called is True
    assert data["houses"][0]["name"] == sample_calender_info.name
    assert data["houses"][0]["is_like"] == sample_calender_info.is_like


def test_house_public_detail_view_when_valid_request_id(
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

    sample_entity = HousePublicDetailEntity(
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
        public_sales=None,
        near_houses=None,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.is_enable_public_sale_house"
    ) as mock_enable:
        mock_enable.return_value = True
        with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_house_public_detail"
        ) as mock_house_public_detail:
            mock_house_public_detail.return_value = sample_entity
            with test_request_context:
                response = client.get(
                    url_for("api/tanos.house_public_detail_view", house_id=1),
                    headers=headers,
                )

    data = response.get_json()["data"]

    assert response.status_code == 200
    assert mock_house_public_detail.called is True
    assert mock_enable.called is True
    assert data["house"]["name"] == sample_entity.name


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
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)
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
    assert data["houses"][0]["image_path"] == public_sale_photo.path


def test_get_ticket_usage_result_view_then_return_usage_ticket_list(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
    create_ticket_usage_results,
    public_sale_photo_factory,
):
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)
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
            url_for("api/tanos.get_ticket_usage_result_view"), headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["houses"]) == 1
    assert data["houses"][0]["image_path"] == public_sale_photo.path
    assert "아파트" in data["houses"][0]["name"]


def test_get_ticket_usage_result_view_then_return_no_list(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
):
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)
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
            url_for("api/tanos.get_ticket_usage_result_view"), headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["houses"]) == 0
