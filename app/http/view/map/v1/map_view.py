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
from http import HTTPStatus

from flask import request, jsonify
from flask_sqlalchemy import BaseQuery
from sqlalchemy import func, select, or_, and_, exists
from sqlalchemy.orm.strategy_options import joinedload, contains_eager, subqueryload

from app.extensions.database import session
from app.extensions.utils.query_helper import RawQueryHelper
from app.http.requests.v1.map_request import GetCoordinatesRequest
from app.http.responses import failure_response
from app.http.responses.presenters.v1.map_presenter import BoundingPresenter
from app.http.view import api
from app.persistence.model import RealEstateModel, RealTradeModel, PreSaleModel, UserInfoModel
from core.domains.map.dto.map_dto import RealEstateWithCoordinateDto
from core.domains.map.use_case.v1.map_use_case import MapBoundingUseCase
from core.exceptions import InvalidRequestException
from core.use_case_output import UseCaseFailureOutput, FailureType


@api.route("/v1/map/bounding", methods=["GET"])
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
    try:
        examples = session.query(RealEstateModel, RealTradeModel, PreSaleModel,
                                 func.ST_X(RealEstateModel.coordinates).label("longitude"),
                                 func.ST_Y(RealEstateModel.coordinates).label("latitude")) \
            .join(RealEstateModel.real_trades, isouter=True) \
            .join(RealEstateModel.pre_sales, isouter=True) \
            .add_entity(RealTradeModel)\
            .add_entity(PreSaleModel)\
            .filter(RealEstateModel.is_available == "True") \
            .filter(func.ST_Contains(func.ST_MakeEnvelope(start_x, end_y, end_x, start_y, 4326),
                                     RealEstateModel.coordinates)).all()

    except Exception as e:
        print("-------------error----------")
        print(e)
    print("query start")
    # RawQueryHelper.print_raw_query(examples)
    print(examples)


    return jsonify(start_x=dto.start_x, start_y=dto.start_y, end_x=dto.end_x, end_y=dto.end_y)
    # return BoundingPresenter().transform(MapBoundingUseCase().execute(dto=dto))
