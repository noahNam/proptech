import json
import uuid
from http import HTTPStatus
from unittest.mock import patch

from flask import url_for

from app.persistence.model import (
    DeviceModel,
    DeviceTokenModel,
    UserModel,
    AppAgreeTermsModel,
    UserProfileModel,
    UserInfoModel, ReceivePushTypeModel,
)
from core.domains.user.dto.user_dto import UpsertUserInfoDetailDto
from core.domains.user.enum.user_info_enum import IsHouseOwnerCodeEnum, CodeEnum, MonthlyIncomeEnum
from core.domains.user.repository.user_repository import UserRepository
from core.use_case_output import FailureType


def test_get_user_view_then_success(
        client, session, test_request_context, make_header, make_authorization, create_users
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_view"),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["user"]["is_required_agree_terms"] is True
    assert data["user"]["is_active"] is True
    assert data["user"]["is_out"] is False


def test_get_user_view_then_user_is_not_found(
        client, session, test_request_context, make_header, make_authorization
):
    authorization = make_authorization(user_id=1)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_view"),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["user"] is None


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
    dict_ = dict(uuid=str(uuid.uuid4()), os="AOS", token=str(uuid.uuid4()), )

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
    assert response.get_json()["message"] == "unauthorized_error"


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
    dict_ = dict(uuid=str(uuid.uuid4()), os="AOS", token=str(uuid.uuid4()), )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_user_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    user = session.query(UserModel).filter_by(id=user_id).first()
    device = session.query(DeviceModel).filter_by(user_id=user_id).first()
    device_token = session.query(DeviceTokenModel).filter_by(id=device.id).first()

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

    # users
    assert user.is_required_agree_terms is False
    assert user.is_active is True
    assert user.is_out is False

    # devices
    assert device.user_id == user_id
    assert device.uuid == dict_["uuid"]
    assert device.os == dict_["os"]
    assert device.is_active is True
    assert device.is_auth is False
    assert device.phone_number is None

    # device_tokens
    assert device_token.device_id == device.id
    assert device_token.token == dict_["token"]


def test_create_app_agree_terms_when_first_login_with_not_receive_marketing_then_success(
        client, session, test_request_context, make_header, make_authorization, create_users
):
    user_id = 1
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(receive_marketing_yn=False, )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_app_agree_terms_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    receive_push_types = session.query(ReceivePushTypeModel).filter_by(user_id=user_id).first()

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"
    assert isinstance(data["result"], str)
    assert receive_push_types.is_marketing is False


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
    dict_ = dict(receive_marketing_yn=False, )

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
    dict_ = dict(receive_marketing_yn=False, )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_app_agree_terms_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    user = session.query(UserModel).filter_by(id=user_id).first()
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
    assert app_agree_terms.receive_marketing_yn is False
    assert app_agree_terms.receive_marketing_date is None


@patch("core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message", return_value=True)
def test_upsert_user_info_view_when_first_input_nickname_then_create_success(
        _send_sqs_message, client, session, test_request_context, make_header, make_authorization, user_factory
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
    dict_ = dict(codes=[1000], values=["noah"])

    with test_request_context:
        response = client.post(
            url_for("api/tanos.upsert_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    user_profile_model = (
        session.query(UserProfileModel).filter_by(user_id=user_id).first()
    )
    user_info_model = (
        session.query(UserInfoModel)
            .filter_by(user_profile_id=user_profile_model.id, code=dict_.get("codes")[0])
            .first()
    )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

    # user_profile_model
    assert user_profile_model.nickname == dict_.get("values")[0]
    assert user_profile_model.last_update_code == dict_.get("codes")[0]
    # user_info_model
    assert user_info_model.user_profile_id == user_profile_model.id
    assert user_info_model.code == dict_.get("codes")[0]
    assert user_info_model.value == dict_.get("values")[0]


@patch("core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message", return_value=True)
def test_upsert_user_info_view_when_input_user_data_then_create_success(
        _send_sqs_message, client, session, test_request_context, make_header, make_authorization, user_factory
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
    dict_ = dict(codes=[1005], values=["2"])

    with test_request_context:
        response = client.post(
            url_for("api/tanos.upsert_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    user_profile_model = (
        session.query(UserProfileModel).filter_by(user_id=user_id).first()
    )
    user_info_model = (
        session.query(UserInfoModel)
            .filter_by(user_profile_id=user_profile_model.id, code=1005)
            .first()
    )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

    # user_profile_model
    assert user_profile_model.last_update_code == dict_.get("codes")[0]
    # user_info_model
    assert user_info_model.user_profile_id == user_profile_model.id
    assert user_info_model.code == dict_.get("codes")[0]
    assert user_info_model.value == dict_.get("values")[0]


@patch("core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message", return_value=True)
def test_upsert_user_info_view_when_input_user_data_then_update_success(
        _send_sqs_message, client, session, test_request_context, make_header, make_authorization, user_factory
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
    dict_ = dict(code=1005, value="2")

    with test_request_context:
        client.post(
            url_for("api/tanos.upsert_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    dict2_ = dict(codes=[1005], values=["1"])

    with test_request_context:
        response = client.post(
            url_for("api/tanos.upsert_user_info_view"),
            data=json.dumps(dict2_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

    user_info_model = (
        session.query(UserInfoModel)
            .filter_by(user_profile_id=1, code=dict2_.get("codes")[0])
            .first()
    )

    # user_info_model
    assert user_info_model.code == dict2_.get("codes")[0]
    assert user_info_model.value == dict2_.get("values")[0]


@patch("core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message", return_value=True)
def test_upsert_user_info_view_when_next_step_input_user_data_then_update_user_last_update_code(
        _send_sqs_message, client, session, test_request_context, make_header, make_authorization, user_factory
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
    dict_ = dict(codes=[1000], values=["noah"])

    with test_request_context:
        client.post(
            url_for("api/tanos.upsert_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    dict2_ = dict(codes=[1005], values=["1"])

    with test_request_context:
        response = client.post(
            url_for("api/tanos.upsert_user_info_view"),
            data=json.dumps(dict2_),
            headers=headers,
        )

    user_profile_model = (
        session.query(UserProfileModel).filter_by(user_id=user_id).first()
    )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

    # user_profile_model
    assert user_profile_model.last_update_code == dict2_.get("codes")[0]


def test_get_user_info_when_no_user_data_with_none_detail_code_then_success(
        client, session, test_request_context, make_header, make_authorization, create_users
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(codes=[1000], )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"][0]["code"] == dict_.get("codes")[0]
    assert data["result"][0]["code_values"] is None
    assert data["result"][0]["user_value"] is None


def test_get_user_info_when_no_user_data_with_detail_code_then_success(
        client, session, test_request_context, make_header, make_authorization, create_users
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(codes=[1005], )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"][0]["code"] == dict_.get("codes")[0]
    assert len(data["result"][0]["code_values"]["detail_code"]) == 3
    assert len(data["result"][0]["code_values"]["name"]) == 3
    assert (
            data["result"][0]["code_values"]["detail_code"]
            == IsHouseOwnerCodeEnum.COND_CD.value
    )
    assert data["result"][0]["code_values"]["name"] == IsHouseOwnerCodeEnum.COND_NM.value


@patch("core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message", return_value=True)
def test_get_user_info_when_exist_user_data_with_detail_code_then_success(
        _send_sqs_message, client, session, test_request_context, make_header, make_authorization, create_users
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(codes=[1005], values=["2"])

    with test_request_context:
        client.post(
            url_for("api/tanos.upsert_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    dict2_ = dict(codes=[1005], )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_info_view"),
            data=json.dumps(dict2_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"][0]["code"] == dict_.get("codes")[0]
    assert data["result"][0]["user_value"] == dict_.get("values")[0]
    assert len(data["result"][0]["code_values"]["detail_code"]) == 3
    assert len(data["result"][0]["code_values"]["name"]) == 3
    assert (
            data["result"][0]["code_values"]["detail_code"]
            == IsHouseOwnerCodeEnum.COND_CD.value
    )
    assert data["result"][0]["code_values"]["name"] == IsHouseOwnerCodeEnum.COND_NM.value


@patch("core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message", return_value=True)
def test_get_user_info_view_when_monthly_income_then_success(
        _send_sqs_message, client, session, test_request_context, make_header, make_authorization, create_users,
        avg_monthly_income_worker_factory
):
    # data set ##################################################################################
    avg_monthly_income_workers = avg_monthly_income_worker_factory.build()
    session.add(avg_monthly_income_workers)
    session.commit()

    # 외벌이, 맞벌이 확인
    # 외벌이 -> 1,3,4 / 맞벌이 -> 2
    upsert_user_info_dto = UpsertUserInfoDetailDto(
        user_id=create_users[0].id, user_profile_id=create_users[0].id, code=CodeEnum.IS_MARRIED.value, value="2"
    )
    UserRepository().create_user_info(dto=upsert_user_info_dto)

    # 부양가족 수
    # 3인 이하->1,2,3 / 4인->4 / 5인->5 / 6인->6 / 7인->7 / 8명 이상->8 / 없어요->9
    upsert_user_info_dto = UpsertUserInfoDetailDto(
        user_id=create_users[0].id, user_profile_id=create_users[0].id, code=CodeEnum.NUMBER_DEPENDENTS.value, value="5"
    )
    UserRepository().create_user_info(dto=upsert_user_info_dto)
    #############################################################################################

    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(codes=[CodeEnum.MONTHLY_INCOME.value])

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"][0]["code"] == dict_.get("codes")[0]
    assert data["result"][0]["user_value"] is None
    assert (
            data["result"][0]["code_values"]["detail_code"]
            == MonthlyIncomeEnum.COND_CD_2.value
    )
    assert len(data["result"][0]["code_values"]["detail_code"]) == len(data["result"][0]["code_values"]["name"])
    # 맞벌이, 부양가족 5인 기준
    assert data["result"][0]["code_values"]["name"] == [3547102, 5675364, 7803626, 8513046, 9222466, 9931887, 11350728]


@patch("core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message", return_value=True)
def test_get_user_info_view_when_get_address_then_success(
        _send_sqs_message, client, session, test_request_context, make_header, make_authorization, create_users,
        create_sido_codes
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(codes=[CodeEnum.ADDRESS.value, CodeEnum.ADDRESS_DETAIL.value])

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"][0]["code"] == dict_.get("codes")[0]
    assert data["result"][0]["user_value"] is None
    assert len(data["result"][0]["code_values"]) == 2
    assert len(data["result"][0]["code_values"]["detail_code"]) == len(data["result"][0]["code_values"]["name"])
    assert len(data["result"][1]["code_values"]["detail_code"]) == len(data["result"][1]["code_values"]["name"])


def test_get_user_info_when_no_user_data_with_detail_code_then_success(
        client, session, test_request_context, make_header, make_authorization, create_users
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(codes=[1005])

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"][0]["code"] == dict_.get("codes")[0]
    assert len(data["result"][0]["code_values"]["detail_code"]) == 3
    assert len(data["result"][0]["code_values"]["name"]) == 3
    assert (
            data["result"][0]["code_values"]["detail_code"]
            == IsHouseOwnerCodeEnum.COND_CD.value
    )
    assert data["result"][0]["code_values"]["name"] == IsHouseOwnerCodeEnum.COND_NM.value


@patch("core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message", return_value=True)
def test_get_user_info_view_when_input_address_then_create_both_data_success(
        _send_sqs_message, client, session, test_request_context, make_header, make_authorization, user_factory,
        create_sido_codes
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
    dict_ = dict(codes=[CodeEnum.ADDRESS.value, CodeEnum.ADDRESS_DETAIL.value], values=["29", "29010"])

    with test_request_context:
        client.post(
            url_for("api/tanos.upsert_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    dict2_ = dict(codes=[CodeEnum.ADDRESS.value, CodeEnum.ADDRESS_DETAIL.value])

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_info_view"),
            data=json.dumps(dict2_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"][0]['code'] == CodeEnum.ADDRESS.value
    assert len(data["result"]) == len(dict2_.get("codes"))
    assert data["result"][0]['user_value'] == dict_.get("values")[0]
    assert data["result"][1]['user_value'] == dict_.get("values")[1]


@patch("core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message", return_value=True)
def test_upsert_user_info_view_when_input_number_of_child_then_create_both_data_success(
        _send_sqs_message, client, session, test_request_context, make_header, make_authorization, user_factory,
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
        codes=[CodeEnum.CHILD_AGE_SIX.value, CodeEnum.CHILD_AGE_NINETEEN.value, CodeEnum.CHILD_AGE_TWENTY.value],
        values=["1", "2", "True"])

    with test_request_context:
        client.post(
            url_for("api/tanos.upsert_user_info_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    dict2_ = dict(
        codes=[CodeEnum.CHILD_AGE_SIX.value, CodeEnum.CHILD_AGE_NINETEEN.value, CodeEnum.CHILD_AGE_TWENTY.value])

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_user_info_view"),
            data=json.dumps(dict2_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"][0]['code'] == CodeEnum.CHILD_AGE_SIX.value
    assert data["result"][1]['code'] == CodeEnum.CHILD_AGE_NINETEEN.value
    assert data["result"][2]['code'] == CodeEnum.CHILD_AGE_TWENTY.value
    assert len(data["result"]) == len(dict2_.get("codes"))
    assert data["result"][0]['user_value'] == dict_.get("values")[0]
    assert data["result"][1]['user_value'] == dict_.get("values")[1]
    assert data["result"][2]['user_value'] == dict_.get("values")[2]
