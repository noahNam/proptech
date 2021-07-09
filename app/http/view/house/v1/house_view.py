# @api.route("/v1/users/terms", methods=["POST"])
# @jwt_required
# @auth_required
# @swag_from("create_app_agree_terms.yml", methods=["POST"])
# def create_app_agree_terms_view():
#     dto = CreateAppAgreeTermsRequestSchema(
#         **request.get_json(), user_id=current_user.id,
#     ).validate_request_and_make_dto()
#
#     return CreateAppAgreeTermsPresenter().transform(
#         CreateAppAgreeTermsUseCase().execute(dto=dto)
#     )
from datetime import date, timedelta, datetime
from http import HTTPStatus

from flask import request, jsonify
from sqlalchemy import func, or_, and_

from app.extensions.database import session
from app.extensions.utils.time_helper import get_month_from_today
from app.http.requests.v1.house_request import GetCoordinatesRequest
from app.http.responses import failure_response
from app.http.responses.presenters.v1.house_presenter import BoundingPresenter
from app.http.view import api
from app.persistence.model import RealEstateModel, PrivateSaleModel, PublicSaleModel, \
    PublicSalePhotoModel, PublicSaleDetailModel
from core.domains.house.use_case.v1.house_use_case import BoundingUseCase
from core.exceptions import InvalidRequestException
from core.use_case_output import UseCaseFailureOutput, FailureType


@api.route("/v1/house/bounding", methods=["GET"])
def bounding_view():
    try:
        start_x = float(request.args.get("start_x"))
        start_y = float(request.args.get("start_y"))
        end_x = float(request.args.get("end_x"))
        end_y = float(request.args.get("end_y"))
        level = int(request.args.get("level"))

    except Exception as e:
        return failure_response(
            UseCaseFailureOutput(
                type=FailureType.INVALID_REQUEST_ERROR,
                message=f"Not enough or Wrong type Parameter, Error: {e} ",
            ),
            status_code=HTTPStatus.BAD_REQUEST,
        )

    try:
        dto = GetCoordinatesRequest(start_x=start_x,
                                    start_y=start_y,
                                    end_x=end_x,
                                    end_y=end_y,
                                    level=level).validate_request_and_make_dto()
    except InvalidRequestException:
        return failure_response(
            UseCaseFailureOutput(
                type=FailureType.INVALID_REQUEST_ERROR,
                message=f"Invalid Parameter input, Only South_Korea boundary coordinates Available",
            )
        )

    return BoundingPresenter().transform(BoundingUseCase().execute(dto=dto))
    # return jsonify(start_x=dto.start_x, start_y=dto.start_y, end_x=dto.end_x, end_y=dto.end_y)
