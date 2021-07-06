import json
from flask import url_for

from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.enum.house_enum import HouseTypeEnum


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
        client, session, test_request_context, make_header, make_authorization, create_users, interest_house_factory
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
