from flasgger import swag_from
from flask import request
from flask_jwt_extended import jwt_required

from app.http.requests.v1.user_request import (
    CreateUserRequestSchema,
    CreateAppAgreeTermsRequestSchema,
    UpsertUserInfoRequestSchema,
    GetUserInfoRequestSchema,
)
from app.http.responses.presenters.v1.user_presenter import (
    CreateUserPresenter,
    CreateAppAgreeTermsPresenter,
    UpsertUserInfoPresenter,
    GetUserInfoPresenter,
)
from app.http.view import auth_required, api, current_user
from core.domains.user.use_case.v1.user_use_case import (
    CreateUserUseCase,
    CreateAppAgreeTermsUseCase,
    UpsertUserInfoUseCase,
    GetUserInfoUseCase,
)


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
