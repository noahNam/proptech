from flasgger import swag_from
from flask import request
from flask_jwt_extended import jwt_required

from app.http.requests.v1.user_request import (
    CreateUserRequestSchema,
    CreateAppAgreeTermsRequestSchema,
    UpsertUserInfoRequestSchema,
    GetUserInfoRequestSchema,
    GetUserRequestSchema,
    GetUserMainRequestSchema,
    GetSurveysRequestSchema,
    UpdateUserProfileRequestSchema,
    GetUserProviderRequestSchema,
    GetMonthlyIncomesRequestSchema,
    UpdateFcmTokenRequestSchema,
)
from app.http.responses.presenters.v1.user_presenter import (
    CreateUserPresenter,
    CreateAppAgreeTermsPresenter,
    UpsertUserInfoPresenter,
    GetUserInfoPresenter,
    GetUserPresenter,
    PatchUserOutPresenter,
    GetUserMainPresenter,
    GetSurveysPresenter,
    GetUserProfilePresenter,
    UpdateUserProfilePresenter,
    GetUserProviderPresenter,
    GetMonthlyIncomesPresenter,
    UpdateFcmTokenPresenter,
)
from app.http.view import auth_required, api, current_user
from core.domains.user.use_case.v1.user_use_case import (
    CreateUserUseCase,
    CreateAppAgreeTermsUseCase,
    UpsertUserInfoUseCase,
    GetUserInfoUseCase,
    GetUserUseCase,
    UserOutUseCase,
    GetUserMainUseCase,
    GetSurveysUseCase,
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
    GetUserProviderUseCase,
    GetMonthlyIncomesUseCase,
    UpdateFcmTokenUseCase,
)


@api.route("/v1/users", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_user.yml", methods=["GET"])
def get_user_view():
    dto = GetUserRequestSchema(user_id=current_user.id,).validate_request_and_make_dto()

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
        survey_step=request.args.get("survey_step"), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetUserInfoPresenter().transform(GetUserInfoUseCase().execute(dto=dto))


@api.route("/v1/users/info/income", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_user_monthly_incomes.yml", methods=["GET"])
def get_user_monthly_incomes_view():
    dto = GetMonthlyIncomesRequestSchema(
        is_married=request.args.get("is_married"),
        number_dependents=request.args.get("number_dependents"),
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetMonthlyIncomesPresenter().transform(
        GetMonthlyIncomesUseCase().execute(dto=dto)
    )


@api.route("/v1/users/provider", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_user_provider.yml", methods=["GET"])
def get_user_provider_view():
    auth_header = request.headers.get("Authorization")

    dto = GetUserProviderRequestSchema(
        user_id=current_user.id, auth_header=auth_header
    ).validate_request_and_make_dto()

    return GetUserProviderPresenter().transform(
        GetUserProviderUseCase().execute(dto=dto)
    )


@api.route("/v1/users/out", methods=["PATCH"])
@jwt_required
@auth_required
@swag_from("patch_user_out.yml", methods=["PATCH"])
def patch_user_out_view():
    dto = GetUserRequestSchema(user_id=current_user.id,).validate_request_and_make_dto()

    return PatchUserOutPresenter().transform(UserOutUseCase().execute(dto=dto))


@api.route("/v1/users/main", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_user_main.yml", methods=["GET"])
def get_user_main_view():
    dto = GetUserMainRequestSchema(
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetUserMainPresenter().transform(GetUserMainUseCase().execute(dto=dto))


@api.route("/v1/users/surveys", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_surveys.yml", methods=["GET"])
def get_surveys_view():
    dto = GetSurveysRequestSchema(
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetSurveysPresenter().transform(GetSurveysUseCase().execute(dto=dto))


@api.route("/v1/users/profile", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_user_profile.yml", methods=["GET"])
def get_user_profile_view():
    dto = GetUserRequestSchema(user_id=current_user.id,).validate_request_and_make_dto()

    return GetUserProfilePresenter().transform(GetUserProfileUseCase().execute(dto=dto))


@api.route("/v1/users/profile", methods=["PATCH"])
@jwt_required
@auth_required
@swag_from("update_user_profile.yml", methods=["PATCH"])
def update_user_profile_view():
    dto = UpdateUserProfileRequestSchema(
        **request.get_json(), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return UpdateUserProfilePresenter().transform(
        UpdateUserProfileUseCase().execute(dto=dto)
    )


@api.route("/v1/users/fcm-token", methods=["PATCH"])
@jwt_required
@auth_required
@swag_from("update-fcm-token.yml", methods=["PATCH"])
def update_fcm_token_view():
    dto = UpdateFcmTokenRequestSchema(
        **request.get_json(), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return UpdateFcmTokenPresenter().transform(UpdateFcmTokenUseCase().execute(dto=dto))
