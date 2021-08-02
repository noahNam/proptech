from flasgger import swag_from

from app.http.requests.v1.payment_request import (
    GetTicketUsageResultRequestSchema,
    UseBasicTicketRequestSchema,
)
from app.http.responses.presenters.v1.payment_presenter import (
    GetTicketUsageResultPresenter,
    UseBasicTicketPresenter,
)
from app.http.view import auth_required, api, current_user, jwt_required
from core.domains.payment.use_case.v1.payment_use_case import (
    GetTicketUsageResultUseCase,
    UseBasicTicketUseCase,
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
# @jwt_required
# @auth_required
@swag_from("use_ticket.yml", methods=["POST"])
def use_basic_ticket_view():
    dto = UseBasicTicketRequestSchema(user_id=1,).validate_request_and_make_dto()

    return UseBasicTicketPresenter().transform(UseBasicTicketUseCase().execute(dto=dto))
