from flasgger import swag_from
from flask import request

from app.http.requests.v1.payment_request import (
    GetTicketUsageResultRequestSchema,
    UseBasicTicketRequestSchema,
    CreateRecommendCodeRequestSchema,
    GetRecommendCodeRequestSchema,
    UseRecommendCodeRequestSchema,
)
from app.http.responses.presenters.v1.payment_presenter import (
    GetTicketUsageResultPresenter,
    UseBasicTicketPresenter,
    CreateRecommendCodePresenter,
    GetRecommendCodePresenter,
    UseRecommendCodePresenter,
)
from app.http.view import auth_required, api, current_user, jwt_required
from core.domains.payment.use_case.v1.payment_use_case import (
    GetTicketUsageResultUseCase,
    UseBasicTicketUseCase,
    CreateRecommendCodeUseCase,
    GetRecommendCodeUseCase,
    UseRecommendCodeUseCase,
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


@api.route("/v1/payments/ticket", methods=["POST"])
@jwt_required
@auth_required
@swag_from("use_ticket.yml", methods=["POST"])
def use_basic_ticket_view():
    dto = UseBasicTicketRequestSchema(
        **request.get_json(), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return UseBasicTicketPresenter().transform(UseBasicTicketUseCase().execute(dto=dto))


@api.route("/v1/payments/recommend-code", methods=["POST"])
@jwt_required
@auth_required
@swag_from("use_ticket.yml", methods=["POST"])
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
@swag_from("use_ticket.yml", methods=["GET"])
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
@swag_from("use_ticket.yml", methods=["POST"])
def use_recommend_code_view(code):
    dto = UseRecommendCodeRequestSchema(
        code=code, user_id=current_user.id,
    ).validate_request_and_make_dto()

    return UseRecommendCodePresenter().transform(
        UseRecommendCodeUseCase().execute(dto=dto)
    )
