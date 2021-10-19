from flasgger import swag_from
from flask import request
from flask_jwt_extended import jwt_required

from app.http.requests.v1.payment_request import (
    GetTicketUsageResultRequestSchema,
    CreateRecommendCodeRequestSchema,
    GetRecommendCodeRequestSchema,
    UseRecommendCodeRequestSchema,
    UseHouseTicketRequestSchema,
    UseUserTicketRequestSchema,
)
from app.http.responses.presenters.v1.payment_presenter import (
    GetTicketUsageResultPresenter,
    CreateRecommendCodePresenter,
    GetRecommendCodePresenter,
    UseRecommendCodePresenter,
    UseHouseTicketPresenter,
    UseUserTicketPresenter,
)
from app.http.view import auth_required, api, current_user
from core.domains.payment.use_case.v1.payment_use_case import (
    GetTicketUsageResultUseCase,
    CreateRecommendCodeUseCase,
    GetRecommendCodeUseCase,
    UseRecommendCodeUseCase,
    UseHouseTicketUseCase,
    UseUserTicketUseCase,
)


@api.route("/v1/payments/ticket", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_ticket_usage_result.yml", methods=["GET"])
def get_ticket_usage_result_view():
    dto = GetTicketUsageResultRequestSchema(
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetTicketUsageResultPresenter().transform(
        GetTicketUsageResultUseCase().execute(dto=dto)
    )


@api.route("/v1/payments/house", methods=["POST"])
@jwt_required
@auth_required
@swag_from("use_ticket_house.yml", methods=["POST"])
def use_house_ticket_view():
    auth_header = request.headers.get("Authorization")

    dto = UseHouseTicketRequestSchema(
        **request.get_json(), user_id=current_user.id, auth_header=auth_header
    ).validate_request_and_make_dto()

    return UseHouseTicketPresenter().transform(UseHouseTicketUseCase().execute(dto=dto))


@api.route("/v1/payments/user", methods=["POST"])
@jwt_required
@auth_required
@swag_from("use_ticket_user.yml", methods=["POST"])
def use_user_ticket_view():
    auth_header = request.headers.get("Authorization")

    dto = UseUserTicketRequestSchema(
        user_id=current_user.id, auth_header=auth_header
    ).validate_request_and_make_dto()

    return UseUserTicketPresenter().transform(UseUserTicketUseCase().execute(dto=dto))


@api.route("/v1/payments/recommend-code", methods=["POST"])
@jwt_required
@auth_required
@swag_from("create_recommend_code.yml", methods=["POST"])
def create_recommend_code_view():
    dto = CreateRecommendCodeRequestSchema(
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return CreateRecommendCodePresenter().transform(
        CreateRecommendCodeUseCase().execute(dto=dto)
    )


@api.route("/v1/payments/recommend-code", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_recommend_code.yml", methods=["GET"])
def get_recommend_code_view():
    dto = GetRecommendCodeRequestSchema(
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetRecommendCodePresenter().transform(
        GetRecommendCodeUseCase().execute(dto=dto)
    )


@api.route("/v1/payments/recommend-code/<string:code>", methods=["POST"])
@jwt_required
@auth_required
@swag_from("use_recommend_code.yml", methods=["POST"])
def use_recommend_code_view(code):
    dto = UseRecommendCodeRequestSchema(
        code=code, user_id=current_user.id,
    ).validate_request_and_make_dto()

    return UseRecommendCodePresenter().transform(
        UseRecommendCodeUseCase().execute(dto=dto)
    )
