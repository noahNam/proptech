import json
from http import HTTPStatus
from unittest.mock import patch

import pytest
from flask import url_for

from app.extensions.utils.enum.cache_enum import RedisKeyPrefix, RedisExpire
from tests.seeder.factory import UserFactory


def test_view_when_user_id_exists_then_check_auth_success(
    client, session, test_request_context, jwt_manager, make_header, make_authorization,
):
    user = UserFactory.build()
    session.add(user)
    session.commit()

    authorization = make_authorization(user_id=user.id)
    headers = make_header(authorization=authorization)

    with test_request_context:
        response = client.get(
            url_for("api/tanos.auth_for_testing_view"), headers=headers
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"


def test_view_when_user_id_not_exists_then_check_auth_failure(
    client, session, test_request_context, jwt_manager, make_header, make_authorization
):
    authorization = make_authorization()
    headers = make_header(authorization=authorization)

    with test_request_context:
        response = client.get(
            url_for("api/tanos.auth_for_testing_view"), headers=headers
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.get_json()["type"] == "unauthorized_error"


@pytest.mark.skip(reason="local redis 실행 안할경우 편의상 skip")
@patch("app.extensions.sens.sms.SmsClient.send_sms")
def test_auth_send_sms_when_first_login_then_success(
    send_sms,
    client,
    test_request_context,
    jwt_manager,
    make_header,
    make_authorization,
):
    send_sms.return_value = dict(status_code=202)
    authorization = make_authorization(user_id=3)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(phone_number="01044744412")

    with test_request_context:
        response = client.post(
            url_for("api/tanos.mobile_auth_sms_send_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"


@pytest.mark.skip(reason="local redis 실행 안할경우 편의상 skip")
def test_auth_send_sms_when_not_input_phone_number_then_error(
    client, test_request_context, jwt_manager, make_header, make_authorization,
):
    authorization = make_authorization(user_id=3)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(phone_number=None)

    with test_request_context:
        response = client.post(
            url_for("api/tanos.mobile_auth_sms_send_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()
    assert response.status_code == 500
    assert data["type"] == 500
    assert data["message"] == "Can not send SMS to NCP"


@pytest.mark.skip(reason="local redis 실행 안할경우 편의상 skip")
@patch("app.extensions.sens.sms.SmsClient.send_sms")
def test_send_sms_view_when_first_login_then_error(
    send_sms,
    client,
    test_request_context,
    jwt_manager,
    make_header,
    make_authorization,
):
    send_sms.return_value = dict(status_code=401, message="Authorization")
    authorization = make_authorization(user_id=3)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(phone_number="01044744412")

    with test_request_context:
        response = client.post(
            url_for("api/tanos.mobile_auth_sms_send_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()
    assert response.status_code == 500
    assert data["type"] == 500
    assert data["message"] == "Can not send SMS to NCP"


@pytest.mark.skip(reason="local redis 실행 안할경우 편의상 skip")
def test_auth_confirm_view_sms_when_input_correct_auth_number_then_success(
    redis,
    client,
    test_request_context,
    jwt_manager,
    make_header,
    make_authorization,
    user_factory,
    session,
):
    # data set
    user = user_factory.build_batch(size=1)
    session.add_all(user)
    session.commit()

    phone_number = "01044744412"
    redis_auth_number = "1234"
    auth_number = "1234"
    key = f"{RedisKeyPrefix.MOBILE_AUTH.value}:{phone_number}"

    redis.set(
        key=key, value=redis_auth_number, ex=RedisExpire.MOBILE_AUTH_TIME.value,
    )

    # execute test code
    authorization = make_authorization(user_id=3)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(phone_number="01044744412", auth_number=auth_number)

    with test_request_context:
        response = client.post(
            url_for("api/tanos.mobile_auth_sms_confirm_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"


@pytest.mark.skip(reason="local redis 실행 안할경우 편의상 skip")
def test_auth_confirm_view_sms_when_input_wrong_number_then_failure(
    redis,
    client,
    test_request_context,
    jwt_manager,
    make_header,
    make_authorization,
    user_factory,
    session,
):
    # data set
    user = user_factory.build_batch(size=1)
    session.add_all(user)
    session.commit()

    phone_number = "01044744412"
    redis_auth_number = "1234"
    auth_number = "1111"
    key = f"{RedisKeyPrefix.MOBILE_AUTH.value}:{phone_number}"

    redis.set(
        key=key, value=redis_auth_number, ex=RedisExpire.MOBILE_AUTH_TIME.value,
    )

    # execute test code
    authorization = make_authorization(user_id=3)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(phone_number="01044744412", auth_number=auth_number)

    with test_request_context:
        response = client.post(
            url_for("api/tanos.mobile_auth_sms_confirm_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "failure"
