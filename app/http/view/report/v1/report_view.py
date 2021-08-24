from flasgger import swag_from
from flask import request

from app.http.requests.v1.report_request import GetExpectedCompetitionRequestSchema
from app.http.responses.presenters.v1.report_presenter import (
    GetExpectedCompetitionPresenter,
)
from app.http.view import auth_required, api, current_user, jwt_required

from core.domains.report.use_case.v1.report_use_case import (
    GetExpectedCompetitionUseCase,
)


@api.route("/v1/report/competition", methods=["GET"])
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
