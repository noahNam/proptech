from http import HTTPStatus

from flasgger import swag_from
from flask import request

from app.http.requests.v1.house_request import (
    GetCoordinatesRequest,
    GetHousePublicDetailRequest,
    GetCalenderInfoRequest
)
from app.http.requests.v1.house_request import UpsertInterestHouseRequestSchema
from app.http.responses import failure_response
from app.http.responses.presenters.v1.house_presenter import (
    BoundingPresenter,
    BoundingAdministrativePresenter,
    GetHousePublicDetailPresenter,
    GetCalenderInfoPresenter,
    UpsertInterestHousePresenter
)
from app.http.view import auth_required, api, current_user, jwt_required
from core.domains.house.enum.house_enum import BoundingLevelEnum, CalenderYearThreshHold
from core.domains.house.use_case.v1.house_use_case import (
    BoundingUseCase,
    GetHousePublicDetailUseCase,
    GetCalenderInfoUseCase
)
from core.domains.house.use_case.v1.house_use_case import UpsertInterestHouseUseCase
from core.exceptions import InvalidRequestException
from core.use_case_output import UseCaseFailureOutput, FailureType


@api.route("/v1/houses/<int:house_id>/like", methods=["POST"])
@jwt_required
@auth_required
@swag_from("upsert_interest_house.yml", methods=["POST"])
def upsert_interest_house_view(house_id):
    dto = UpsertInterestHouseRequestSchema(
        house_id=house_id, user_id=current_user.id, **request.get_json()
    ).validate_request_and_make_dto()

    return UpsertInterestHousePresenter().transform(UpsertInterestHouseUseCase().execute(dto=dto))


@api.route("/v1/houses/bounding", methods=["GET"])
@jwt_required
@auth_required
@swag_from("bounding_view.yml", methods=["GET"])
def bounding_view():
    try:
        start_x = request.args.get("start_x")
        start_y = request.args.get("start_y")
        end_x = request.args.get("end_x")
        end_y = request.args.get("end_y")
        level = request.args.get("level")

    except Exception as e:
        return failure_response(
            UseCaseFailureOutput(
                type=FailureType.INVALID_REQUEST_ERROR,
                message=f"Not enough or Wrong type Parameter, Error: {e} ",
            ),
            status_code=HTTPStatus.BAD_REQUEST,
        )

    try:
        dto = GetCoordinatesRequest(start_x=float(start_x),
                                    start_y=float(start_y),
                                    end_x=float(end_x),
                                    end_y=float(end_y),
                                    level=int(level)).validate_request_and_make_dto()
    except InvalidRequestException:
        return failure_response(
            UseCaseFailureOutput(
                type=FailureType.INVALID_REQUEST_ERROR,
                message=f"Invalid Parameter input, Only South_Korea boundary coordinates Available",
            )
        )
    if dto.level < BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value:
        # level 14 이하 : 행정구역 Presenter 변경
        return BoundingAdministrativePresenter().transform(BoundingUseCase().execute(dto=dto))
    return BoundingPresenter().transform(BoundingUseCase().execute(dto=dto))


@api.route("/v1/houses/public/<int:house_id>", methods=["GET"])
@jwt_required
@auth_required
def house_public_detail_view(house_id: int):
    dto = GetHousePublicDetailRequest(house_id=house_id,
                                      user_id=current_user.id).validate_request_and_make_dto()

    return GetHousePublicDetailPresenter().transform(GetHousePublicDetailUseCase().execute(dto=dto))


@api.route("/v1/houses/calender", methods=["GET"])
@jwt_required
@auth_required
def house_calender_list_view():
    try:
        year = request.args.get("year")
        month = request.args.get("month")
        user_id = current_user.id

    except Exception as e:
        return failure_response(
            UseCaseFailureOutput(
                type=FailureType.INVALID_REQUEST_ERROR,
                message=f"Not enough or Wrong type Parameter, Error: {e} ",
            ),
            status_code=HTTPStatus.BAD_REQUEST,
        )

    try:
        dto = GetCalenderInfoRequest(year=year, month=month, user_id=user_id).validate_request_and_make_dto()
    except InvalidRequestException:
        return failure_response(
            UseCaseFailureOutput(
                type=FailureType.INVALID_REQUEST_ERROR,
                message=f"Invalid Parameter input, "
                        f"year: {CalenderYearThreshHold.MIN_YEAR.value} ~ {CalenderYearThreshHold.MAX_YEAR.value}, "
                        f"month: 1 ~ 12 required",
            )
        )
    return GetCalenderInfoPresenter().transform(GetCalenderInfoUseCase().execute(dto=dto))
