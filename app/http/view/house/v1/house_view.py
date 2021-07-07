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
from sqlalchemy import func, select, or_, and_, exists, funcfilter

from app.extensions.database import session
from app.extensions.utils.query_helper import RawQueryHelper
from app.extensions.utils.time_helper import get_month_from_today
from app.http.requests.v1.house_request import GetCoordinatesRequest
from app.http.responses import failure_response
from app.http.view import api
from app.persistence.model import RealEstateModel, UserInfoModel, PrivateSaleModel, PublicSaleModel, \
    PublicSalePhotoModel, PublicSaleDetailModel
from core.domains.house.dto.house_dto import BoundingDataDto, BoundingOuterDto
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
    query = (
        # PrivateSale : 오늘 날짜 기준 1달 이내 불러오기 완료
        # PublicSale(분양모델)인 경우만 해당 세부 테이블 불러오기 완료
        # 각 경우의 수 별로 사용 가능한 것만 필터링 완료
        # PrivateSale : 불러온 1달 이내 자료에서 평균값 -> 전세의 경우 rent_type=전세인 항목만 골라서 평균 (미완료)
        # PublicSale : 불러온 자료 내 Detail 테이블 평균 -> (미완료)
        # Query list -> pydantic 모델화 (validation 문제로 변경 힘듬)
        # 추가되어야할 column : 취득세 최소 - 최대, 행정구역 - short_name
        session.query(RealEstateModel)
            .join(RealEstateModel.private_sales, isouter=True)
            .join(RealEstateModel.public_sales, isouter=True)
            .join(PublicSaleModel.public_sale_details, isouter=True)
            .join(PublicSaleModel.public_sale_photos, isouter=True)
            .with_entities(RealEstateModel,
                           func.ST_Y(RealEstateModel.coordinates).label("latitude"),
                           func.ST_X(RealEstateModel.coordinates).label("longitude"),
                           PrivateSaleModel,
                           PublicSaleModel,
                           PublicSaleDetailModel,
                           PublicSalePhotoModel)
            .filter(or_(and_(RealEstateModel.is_available == "True",
                             PrivateSaleModel.is_available == "True",
                             PrivateSaleModel.contract_date >= get_month_from_today(),
                             PrivateSaleModel.contract_date <= date.today()),
                        and_(RealEstateModel.is_available == "True",
                             PublicSaleModel.is_available == "True"),
                        and_(RealEstateModel.is_available == "True",
                             PrivateSaleModel.is_available == "True",
                             PublicSaleModel.is_available == "True",
                             PrivateSaleModel.contract_date >= get_month_from_today(),
                             PrivateSaleModel.contract_date <= date.today())))
            .filter(func.ST_Contains(func.ST_MakeEnvelope(start_x, end_y, end_x, start_y, 4326),
                                     RealEstateModel.coordinates))

    )

    real_estates_list = []

    coords = []
    private_sales_list = []
    public_sales_list = []
    public_sales_detail_list = []
    public_sales_photo_list = []
    try:

        results = query.all()

        for result in results:
            # parsing 필요
            print(result)

    except Exception as e:
        print("-------------error----------")
        print(e)

    return jsonify(start_x=dto.start_x, start_y=dto.start_y, end_x=dto.end_x, end_y=dto.end_y)
    # return BoundingPresenter().transform(MapBoundingUseCase().execute(dto=dto))
