from flasgger import swag_from
from flask import request

from app.http.requests.v1.house_request import (
    GetCoordinatesRequestSchema,
    GetHousePublicDetailRequestSchema,
    GetCalenderInfoRequestSchema,
    GetInterestHouseListRequestSchema,
    GetRecentViewListRequestSchema, GetTicketUsageResultRequestSchema,
)
from app.http.requests.v1.house_request import UpsertInterestHouseRequestSchema
from app.http.responses import failure_response
from app.http.responses.presenters.v1.house_presenter import (
    BoundingPresenter,
    BoundingAdministrativePresenter,
    GetHousePublicDetailPresenter,
    GetCalenderInfoPresenter,
    UpsertInterestHousePresenter,
    GetInterestHouseListPresenter,
    GetRecentViewListPresenter, GetTicketUsageResultPresenter,
)
from app.http.view import auth_required, api, current_user, jwt_required
from core.domains.house.enum.house_enum import BoundingLevelEnum, CalenderYearThreshHold
from core.domains.house.use_case.v1.house_use_case import (
    BoundingUseCase,
    GetHousePublicDetailUseCase,
    GetCalenderInfoUseCase,
    GetInterestHouseListUseCase,
    GetRecentViewListUseCase, GetTicketUsageResultUseCase,
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

    return UpsertInterestHousePresenter().transform(
        UpsertInterestHouseUseCase().execute(dto=dto)
    )


@api.route("/v1/houses/map", methods=["GET"])
@jwt_required
@auth_required
@swag_from("bounding_view.yml", methods=["GET"])
def bounding_view():
    try:
        dto = GetCoordinatesRequestSchema(
            start_x=float(request.args.get("start_x")),
            start_y=float(request.args.get("start_y")),
            end_x=float(request.args.get("end_x")),
            end_y=float(request.args.get("end_y")),
            level=int(request.args.get("level")),
        ).validate_request_and_make_dto()
    except InvalidRequestException:
        return failure_response(
            UseCaseFailureOutput(
                type=FailureType.INVALID_REQUEST_ERROR,
                message=f"Invalid Parameter input, Only South_Korea boundary coordinates Available",
            )
        )
    if dto.level < BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value:
        # level 14 이하 : 행정구역 Presenter 변경
        return BoundingAdministrativePresenter().transform(
            BoundingUseCase().execute(dto=dto)
        )
    return BoundingPresenter().transform(BoundingUseCase().execute(dto=dto))


@api.route("/v1/houses/public/<int:house_id>", methods=["GET"])
@jwt_required
@auth_required
@swag_from("house_public_detail_view.yml", methods=["GET"])
def house_public_detail_view(house_id: int):
    dto = GetHousePublicDetailRequestSchema(
        house_id=house_id, user_id=current_user.id
    ).validate_request_and_make_dto()

    return GetHousePublicDetailPresenter().transform(
        GetHousePublicDetailUseCase().execute(dto=dto)
    )


@api.route("/v1/houses/calender", methods=["GET"])
@jwt_required
@auth_required
@swag_from("house_calender_list_view.yml", methods=["GET"])
def house_calender_list_view():
    try:
        dto = GetCalenderInfoRequestSchema(
            year=request.args.get("year"),
            month=request.args.get("month"),
            user_id=current_user.id,
        ).validate_request_and_make_dto()
    except InvalidRequestException:
        return failure_response(
            UseCaseFailureOutput(
                type=FailureType.INVALID_REQUEST_ERROR,
                message=f"Invalid Parameter input, "
                f"year: {CalenderYearThreshHold.MIN_YEAR.value} ~ {CalenderYearThreshHold.MAX_YEAR.value}, "
                f"month: 1 ~ 12 required",
            )
        )
    return GetCalenderInfoPresenter().transform(
        GetCalenderInfoUseCase().execute(dto=dto)
    )


@api.route("/v1/houses/like", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_interest_house_list.yml", methods=["GET"])
def get_interest_house_list_view():
    dto = GetInterestHouseListRequestSchema(
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetInterestHouseListPresenter().transform(
        GetInterestHouseListUseCase().execute(dto=dto)
    )


@api.route("/v1/houses/recent", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_recent_view_list.yml", methods=["GET"])
def get_recent_view_list_view():
    dto = GetRecentViewListRequestSchema(
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetRecentViewListPresenter().transform(
        GetRecentViewListUseCase().execute(dto=dto)
    )


@api.route("/v1/houses/ticket", methods=["GET"])
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
