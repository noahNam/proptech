from flasgger import swag_from
from flask import request

from app.http.requests.v1.report_request import (
    GetExpectedCompetitionRequestSchema,
    GetSaleInfoRequestSchema,
    GetRecentlySaleRequestSchema,
    GetUserSurveysRequestSchema,
)
from app.http.responses.presenters.v1.report_presenter import (
    GetExpectedCompetitionPresenter,
    GetSaleInfoPresenter,
    GetRecentlySalePresenter,
    GetUserSurveysPresenter,
)
from app.http.view import auth_required, api, current_user, jwt_required

from core.domains.report.use_case.v1.report_use_case import (
    GetExpectedCompetitionUseCase,
    GetSaleInfoUseCase,
    GetRecentlySaleUseCase,
    GetUserSurveysUseCase,
)


@api.route("/v1/reports/competition", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_expected_competition.yml", methods=["GET"])
def get_expected_competition_view():
    dto = GetExpectedCompetitionRequestSchema(
        user_id=current_user.id, house_id=request.args.get("house_id"),
    ).validate_request_and_make_dto()

    return GetExpectedCompetitionPresenter().transform(
        GetExpectedCompetitionUseCase().execute(dto=dto)
    )


@api.route("/v1/reports/sale-info", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_sale_info.yml", methods=["GET"])
def get_sale_info_view():
    dto = GetSaleInfoRequestSchema(
        user_id=current_user.id, house_id=request.args.get("house_id"),
    ).validate_request_and_make_dto()

    return GetSaleInfoPresenter().transform(GetSaleInfoUseCase().execute(dto=dto))


@api.route("/v1/reports/recently-sale", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_recently_sale.yml", methods=["GET"])
def get_recently_sale_view():
    dto = GetRecentlySaleRequestSchema(
        user_id=current_user.id, house_id=request.args.get("house_id"),
    ).validate_request_and_make_dto()

    return GetRecentlySalePresenter().transform(
        GetRecentlySaleUseCase().execute(dto=dto)
    )


@api.route("/v1/reports/user-surveys", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_user_surveys.yml", methods=["GET"])
def get_user_surveys_view():
    dto = GetUserSurveysRequestSchema(user_id=current_user.id,).validate_request_and_make_dto()

    return GetUserSurveysPresenter().transform(GetUserSurveysUseCase().execute(dto=dto))
