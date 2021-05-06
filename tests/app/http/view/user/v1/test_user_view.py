import io
import json
from http import HTTPStatus
from unittest.mock import patch
from flask import url_for
from werkzeug.datastructures import FileStorage

from core.use_case_output import FailureType


@patch("app.extensions.utils.image_helper.S3Helper.upload", return_value=True)
def test_create_user_when_first_login_then_success(
        s3_upload_mock,
        client,
        session,
        test_request_context,
        make_header,
        make_authorization,
):
    # 실제 업로드 확인하려면 아래 경로에 이미지 첨부하고 patch 데코레이터 제거한 뒤 실행.
    file_name = "/Users/noah/Downloads/profile_picture/noah.jpg"
    with io.open(file_name, "rb", buffering=0) as temp:
        file = FileStorage(
            stream=temp,
            filename=file_name,
            content_type="multipart/form-data",
        )
        user_id = 1
        authorization = make_authorization(user_id=user_id)
        headers = make_header(
            authorization=authorization, content_type="multipart/form-data", accept="application/json"
        )
        dict_ = dict(
            id=user_id,
            nickname="Tester",
            email="test@gmail.com",
            birthday="19850509",
            gender="M",
            region_ids=json.dumps([1, 2]),
            files=[file],
        )

        with test_request_context:
            response = client.post(
                url_for("api/tanos.create_user_view"), data=dict_, headers=headers
            )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["user"]["nickname"] == "Tester"
    assert isinstance(data["user"]["nickname"], str)


@patch("app.extensions.utils.image_helper.S3Helper.upload", return_value=False)
def test_create_user_when_s3_upload_fail_then_success(
        s3_upload_mock,
        client,
        session,
        test_request_context,
        make_header,
        make_authorization,
):
    file_name = "/Users/noah/Downloads/profile_picture/noah.jpg"
    with io.open(file_name, "rb", buffering=0) as temp:
        file = FileStorage(
            stream=temp,
            filename=file_name,
            content_type="multipart/form-data",
        )
        user_id = 1
        authorization = make_authorization(user_id=user_id)
        headers = make_header(
            authorization=authorization, content_type="multipart/form-data", accept="application/json"
        )
        dict_ = dict(
            id=user_id,
            nickname="Tester",
            email="test@gmail.com",
            birthday="19850509",
            gender="M",
            region_ids=json.dumps([1, 2]),
            files=[file],
        )

        with test_request_context:
            response = client.post(
                url_for("api/tanos.create_user_view"), data=dict_, headers=headers
            )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["user"]["nickname"] == "Tester"
    assert isinstance(data["user"]["nickname"], str)


def test_create_user_when_given_wrong_token_then_unauthorized_error(
        client,
        session,
        test_request_context,
        make_header,
        make_authorization,
):
    user_id = None
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization, content_type="multipart/form-data", accept="application/json"
    )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_user_view"), data=dict(), headers=headers
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.get_json()["type"] == FailureType.UNAUTHORIZED_ERROR
