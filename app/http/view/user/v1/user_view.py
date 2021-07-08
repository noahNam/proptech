from http import HTTPStatus

import requests
from flasgger import swag_from
from flask import request, jsonify

from app.http.requests.v1.user_request import (
    CreateUserRequestSchema,
    CreateAppAgreeTermsRequestSchema,
    UpsertUserInfoRequestSchema,
    GetUserInfoRequestSchema, GetUserRequestSchema,
)
from app.http.responses.presenters.v1.user_presenter import (
    CreateUserPresenter,
    CreateAppAgreeTermsPresenter,
    UpsertUserInfoPresenter,
    GetUserInfoPresenter, GetUserPresenter,
)
from app.http.view import auth_required, api, current_user, jwt_required
from core.domains.user.enum.user_enum import UserProviderCallEnum
from core.domains.user.use_case.v1.user_use_case import (
    CreateUserUseCase,
    CreateAppAgreeTermsUseCase,
    UpsertUserInfoUseCase,
    GetUserInfoUseCase, GetUserUseCase,
)


@api.route("/v1/users", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_user.yml", methods=["GET"])
def get_user_view():
    dto = GetUserRequestSchema(
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetUserPresenter().transform(GetUserUseCase().execute(dto=dto))


@api.route("/v1/users", methods=["POST"])
@jwt_required
@auth_required
@swag_from("create_user.yml", methods=["POST"])
def create_user_view():
    dto = CreateUserRequestSchema(
        **request.get_json(), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return CreateUserPresenter().transform(CreateUserUseCase().execute(dto=dto))


@api.route("/v1/users/terms", methods=["POST"])
@jwt_required
@auth_required
@swag_from("create_app_agree_terms.yml", methods=["POST"])
def create_app_agree_terms_view():
    dto = CreateAppAgreeTermsRequestSchema(
        **request.get_json(), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return CreateAppAgreeTermsPresenter().transform(
        CreateAppAgreeTermsUseCase().execute(dto=dto)
    )


@api.route("/v1/users/info", methods=["POST"])
@jwt_required
@auth_required
@swag_from("upsert_user_info.yml", methods=["POST"])
def upsert_user_info_view():
    dto = UpsertUserInfoRequestSchema(
        **request.get_json(), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return UpsertUserInfoPresenter().transform(UpsertUserInfoUseCase().execute(dto=dto))


@api.route("/v1/users/info", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_user_info.yml", methods=["GET"])
def get_user_info_view():
    dto = GetUserInfoRequestSchema(
        **request.get_json(), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetUserInfoPresenter().transform(GetUserInfoUseCase().execute(dto=dto))


@api.route("/v1/users/provider", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_user_info.yml", methods=["GET"])
def get_user_provider_view():
    auth_header = request.headers.get("Authorization")

    try:
        response = requests.get(
            url=UserProviderCallEnum.CAPTAIN_BASE_URL.value + UserProviderCallEnum.CALL_END_POINT.value,
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Authorization": auth_header
            },
        )
    except Exception:
        raise Exception

    data = response.json()
    return jsonify(data), HTTPStatus.OK
