import json
import uuid
from http import HTTPStatus
from flask import url_for

from app.persistence.model import InterestRegionModel, InterestRegionGroupModel, DeviceModel, DeviceTokenModel, \
    UserModel
from core.use_case_output import FailureType


def test_create_user_when_first_login_then_success(
        client, session, test_request_context, make_header, make_authorization,
):
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(
        region_ids=json.dumps([1]),
        uuid=str(uuid.uuid4()),
        os="AOS",
        token=str(uuid.uuid4()),
    )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_user_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"
    assert isinstance(data["result"], str)


def test_create_user_when_given_wrong_token_then_unauthorized_error(
        client, session, test_request_context, make_header, make_authorization,
):
    user_id = None
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="multipart/form-data",
        accept="application/json",
    )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_user_view"), data=dict(), headers=headers
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.get_json()["type"] == HTTPStatus.UNAUTHORIZED
    assert response.get_json()["message"] == FailureType.UNAUTHORIZED_ERROR


def test_create_user_to_verify_data_when_first_login_tehn_success(
        client, session, test_request_context, make_header, make_authorization, create_interest_region_groups
):
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(
        region_ids=json.dumps([1]),
        uuid=str(uuid.uuid4()),
        os="AOS",
        token=str(uuid.uuid4()),
    )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_user_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    user = (
        session.query(UserModel).filter_by(id=user_id).first()
    )
    interest_region = (
        session.query(InterestRegionModel).filter_by(user_id=user_id).first()
    )
    interest_region_group = (
        session.query(InterestRegionGroupModel).filter_by(id=interest_region.id).first()
    )
    device = (
        session.query(DeviceModel).filter_by(user_id=user_id).first()
    )
    device_token = (
        session.query(DeviceTokenModel).filter_by(id=device.id).first()
    )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

    # users
    assert user.is_required_agree_terms is False
    assert user.is_active is True
    assert user.is_out is False

    # interest_regions
    assert interest_region.user_id == user_id
    assert interest_region.region_id == 1
    assert interest_region_group.interest_count == 1

    # devices
    assert device.user_id == user_id
    assert device.uuid == dict_['uuid']
    assert device.os == dict_['os']
    assert device.is_active is True
    assert device.is_auth is False
    assert device.phone_number is None

    # device_tokens
    assert device_token.device_id == device.id
    assert device_token.token == dict_['token']
