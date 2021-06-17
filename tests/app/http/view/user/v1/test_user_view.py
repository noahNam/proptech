import json
import uuid
from http import HTTPStatus

from flask import url_for

from app.persistence.model import DeviceModel, DeviceTokenModel, \
    UserModel, AppAgreeTermsModel
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
        client, session, test_request_context, make_header, make_authorization
):
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(
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


def test_create_app_agree_terms_when_first_login_with_not_receipt_marketing_then_success(
        client, session, test_request_context, make_header, make_authorization, create_users
):
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(
        receipt_marketing_yn=False,
    )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_app_agree_terms_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"
    assert isinstance(data["result"], str)


def test_create_app_agree_terms_when_first_login_with_not_user_id_then_authorization_error(
        client, session, test_request_context, make_header, make_authorization, create_users
):
    user_id = None
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(
        receipt_marketing_yn=False,
    )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_app_agree_terms_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()
    assert response.status_code == 401
    assert data["type"] == 401
    assert data["message"] == "unauthorized_error"


def test_create_app_agree_terms_to_verify_data_when_first_login_then_success(
        client, session, test_request_context, make_header, make_authorization, user_factory
):
    user_id = 1
    user = user_factory.build(id=user_id, is_required_agree_terms=False)
    session.add(user)
    session.commit()

    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(
        receipt_marketing_yn=False,
    )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_app_agree_terms_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    user = (
        session.query(UserModel).filter_by(id=user_id).first()
    )
    app_agree_terms = (
        session.query(AppAgreeTermsModel).filter_by(user_id=user_id).first()
    )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

    # user
    assert user.is_required_agree_terms is True
    # app_agree_terms
    assert app_agree_terms.user_id == user_id
    assert app_agree_terms.private_user_info_yn is True
    assert app_agree_terms.required_terms_yn is True
    assert app_agree_terms.receipt_marketing_yn is False
    assert app_agree_terms.receipt_marketing_date is None
