from typing import Optional

from sqlalchemy import and_, func, or_, literal, String

from app.extensions.utils.query_helper import RawQueryHelper
from app.extensions.utils.time_helper import get_month_from_today, get_server_timestamp
from app.persistence.model import RealEstateModel, PrivateSaleModel, PublicSaleModel
from core.domains.house.dto.house_dto import CoordinatesRangeDto
from sqlalchemy import exc
from app.extensions.utils.log_helper import logger_
from app.extensions.database import session
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.enum.house_enum import HouseTypeEnum
from core.exceptions import NotUniqueErrorException

logger = logger_.getLogger(__name__)


class HouseRepository:
    def create_interest_house(self, dto: UpsertInterestHouseDto) -> None:
        try:
            interest_house = InterestHouseModel(
                user_id=dto.user_id,
                house_id=dto.house_id,
                type=dto.type,
                is_like=True
            )

            session.add(interest_house)
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][create_like_house] house_id : {dto.house_id} error : {e}"
            )
            raise NotUniqueErrorException

    def update_interest_house(self, dto: UpsertInterestHouseDto) -> int:
        filters = list()
        filters.append(InterestHouseModel.user_id == dto.user_id)
        filters.append(InterestHouseModel.house_id == dto.house_id)
        filters.append(InterestHouseModel.type == dto.type)

        try:
            interest_house = session.query(InterestHouseModel).filter(*filters).update(
                {"is_like": dto.is_like, "updated_at": get_server_timestamp()}
            )
            session.commit()

            return interest_house
        except Exception as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][update_is_like_house] house_id : {dto.house_id} error : {e}"
            )

    def _make_object_bounding_entity_from_queryset(self, queryset: Optional[list]) -> Optional[list]:
        if not queryset:
            return None

        # Make Entity
        results = list()
        for query in queryset:
            results.append(query.to_bounding_entity())
        return results

    def get_queryset_by_coordinates_range_dto(self, dto: CoordinatesRangeDto) -> Optional[list]:
        query = (
            session.query(RealEstateModel)
                .join(RealEstateModel.private_sales, isouter=True)
                .join(RealEstateModel.public_sales, isouter=True)
                .join(PublicSaleModel.public_sale_details, isouter=True)
                .join(PublicSaleModel.public_sale_photos, isouter=True)
                .filter(or_(and_(RealEstateModel.is_available == "True",
                                 PrivateSaleModel.is_available == "True",
                                 PrivateSaleModel.contract_date >= get_month_from_today(),
                                 PrivateSaleModel.contract_date <= get_server_timestamp()),
                            and_(RealEstateModel.is_available == "True",
                                 PublicSaleModel.is_available == "True"),
                            and_(RealEstateModel.is_available == "True",
                                 PrivateSaleModel.is_available == "True",
                                 PublicSaleModel.is_available == "True",
                                 PrivateSaleModel.contract_date >= get_month_from_today(),
                                 PrivateSaleModel.contract_date <= get_server_timestamp())))
                .filter(func.ST_Contains(func.ST_MakeEnvelope(dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326),
                                         RealEstateModel.coordinates))

        )
        queryset = query.all()
        return self._make_object_bounding_entity_from_queryset(queryset=queryset)

    def get_interest_house_list(self, user_id: int) -> None:
        # public_sales_query = (
        #     session.query(InterestHouseModel.id, InterestHouseModel.type,
        #                   PublicSaleModel.name,
        #                   RealEstateModel.road_name, PublicSaleModel.subscription_start_date,
        #                   PublicSaleModel.subscription_end_date)
        #         .join(PublicSaleModel,
        #               (InterestHouseModel.house_id == PublicSaleModel.id) &
        #               (InterestHouseModel.type == HouseTypeEnum.PUBLIC_SALES.value) &
        #               (InterestHouseModel.user_id == user_id) &
        #               (InterestHouseModel.is_like == True)
        #               )
        #         .join(PublicSaleModel.real_estates)
        # )
        #
        # private_sales_query = (
        #     session.query(InterestHouseModel.id, InterestHouseModel.type,
        #                   RealEstateModel.name,
        #                   RealEstateModel.road_name, literal("", String).label("subscription_start_date"),
        #                   literal("", String).label("subscription_end_date"))
        #         .join(PrivateSaleModel,
        #               (InterestHouseModel.house_id == PrivateSaleModel.id) &
        #               (InterestHouseModel.type == HouseTypeEnum.PRIVATE_SALES.value) &
        #               (InterestHouseModel.user_id == user_id) &
        #               (InterestHouseModel.is_like == True)
        #               )
        #         .join(PrivateSaleModel.real_estates)
        # )

        public_sales_query = (
            session.query(InterestHouseModel.id, InterestHouseModel.type,
                          PublicSaleModel.name,
                          RealEstateModel.road_name, PublicSaleModel.subscription_start_date,
                          PublicSaleModel.subscription_end_date)
                .join(PublicSaleModel,
                      (InterestHouseModel.house_id == PublicSaleModel.id) &
                      (InterestHouseModel.type == HouseTypeEnum.PUBLIC_SALES.value) &
                      (InterestHouseModel.user_id == user_id) &
                      (InterestHouseModel.is_like == True)
                      )
                .join(PublicSaleModel.real_estates)
        )

        private_sales_query = (
            session.query(InterestHouseModel.id, InterestHouseModel.type,
                          RealEstateModel.name,
                          RealEstateModel.road_name, literal("", String).label("subscription_start_date"),
                          literal("", String).label("subscription_end_date"))
                .join(PrivateSaleModel,
                      (InterestHouseModel.house_id == PrivateSaleModel.id) &
                      (InterestHouseModel.type == HouseTypeEnum.PRIVATE_SALES.value) &
                      (InterestHouseModel.user_id == user_id) &
                      (InterestHouseModel.is_like == True)
                      )
                .join(PrivateSaleModel.real_estates)
        )

        query = public_sales_query.union_all(private_sales_query)
        # RawQueryHelper.print_raw_query(public_sales_query)
        # RawQueryHelper.print_raw_query(private_sales_query)
        RawQueryHelper.print_raw_query(query)
        queryset = query.all()

        test = 1
