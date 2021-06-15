import json
import uuid
from http import HTTPStatus
from flask import url_for

from core.use_case_output import FailureType


def test_create_user_when_first_login_then_success(
        client,
        session,
        test_request_context,
        make_header,
        make_authorization,
):
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(
        home_owner_type=1,
        interested_house_type=2,
        region_ids=json.dumps([1]),
        uuid=str(uuid.uuid4()),
        os="AOS",
        token=str(uuid.uuid4())
    )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_user_view"), data=json.dumps(dict_), headers=headers
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
