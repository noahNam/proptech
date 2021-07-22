import json
from unittest.mock import patch

from flask import url_for

from app.extensions.utils.time_helper import get_server_timestamp
from app.http.responses import success_response
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.entity.house_entity import BoundingRealEstateEntity, AdministrativeDivisionEntity
from core.domains.house.enum.house_enum import HouseTypeEnum, BoundingLevelEnum, DivisionLevelEnum


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
        client, session, test_request_context, make_header, make_authorization, interest_house_factory
):
    interest_house = interest_house_factory.build()
    session.add(interest_house)

    session.commit()

    upsert_interest_house_dto = UpsertInterestHouseDto(
        user_id=1,
        house_id=1,
        type=HouseTypeEnum.PUBLIC_SALES.value,
        is_like=True
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
            url_for("api/tanos.upsert_interest_house_view", house_id=upsert_interest_house_dto.house_id),
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
        create_real_estate_with_bounding
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
    start_x = 126.5,
    start_y = 37.7,
    end_x = 127.9,
    end_y = 37.42,
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
        public_sales=None
    )

    with patch("app.http.responses.presenters.v1.house_presenter.BoundingPresenter.transform") as mock_result:
        mock_result.return_value = success_response(result=bounding_entitiy.dict())
        with patch(
                "core.domains.house.repository.house_repository.HouseRepository.get_bounding_by_coordinates_range_dto"
        ) as mock_get_bounding:
            mock_get_bounding.return_value = create_real_estate_with_bounding
            with test_request_context:
                response = client.get(
                    url_for("api/tanos.bounding_view",
                            start_x=start_x,
                            start_y=start_y,
                            end_x=end_x,
                            end_y=end_y,
                            level=level), headers=headers)
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
        create_real_estate_with_bounding
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
    start_x = 126.5,
    start_y = 37.7,
    end_x = 127.9,
    end_y = 37.42,
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
        updated_at=get_server_timestamp()
    )

    with patch("app.http.responses.presenters.v1.house_presenter.BoundingAdministrativePresenter.transform") as mock_result:
        mock_result.return_value = success_response(result=bounding_entitiy.dict())
        with patch(
                "core.domains.house.repository.house_repository.HouseRepository.get_administrative_by_coordinates_range_dto"
        ) as mock_get_bounding:
            mock_get_bounding.return_value = create_real_estate_with_bounding
            with test_request_context:
                response = client.get(
                    url_for("api/tanos.bounding_view",
                            start_x=start_x,
                            start_y=start_y,
                            end_x=end_x,
                            end_y=end_y,
                            level=level), headers=headers)
    data = response.get_json()
    assert response.status_code == 200
    assert data["id"] == bounding_entitiy.id
    assert data["name"] == bounding_entitiy.name
    assert mock_get_bounding.called is True
    assert mock_result.called is True
