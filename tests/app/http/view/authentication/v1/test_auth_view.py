from http import HTTPStatus

from flask import url_for

from core.use_case_output import FailureType
from tests.seeder.factory import UserFactory


def test_view_when_user_id_exists_then_check_auth_success(
    client,
    session,
    test_request_context,
    jwt_manager,
    make_header,
    make_authorization,
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

    assert response.status_code == 200
    assert response.json["data"]["result"]["type"] == "success"
    assert response.json["meta"]["cursor"] is None


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
    assert response.get_json()["detail"] == HTTPStatus.UNAUTHORIZED
    assert response.get_json()["message"] == FailureType.UNAUTHORIZED_ERROR
