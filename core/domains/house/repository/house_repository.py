from typing import Optional
from sqlalchemy import and_, func, or_
from app.extensions.utils.time_helper import get_month_from_today, get_server_timestamp
from app.persistence.model import (
    RealEstateModel,
    PrivateSaleModel,
    PublicSaleModel,
    AdministrativeDivisionModel,
    PublicSaleDetailModel
)
from core.domains.house.dto.house_dto import CoordinatesRangeDto
from sqlalchemy import exc
from app.extensions.utils.log_helper import logger_
from app.extensions.database import session
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
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
                {"is_like": dto.is_like}
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
            results.append(query[0].to_bounding_entity(avg_trade=query[1],
                                                       avg_deposit=query[2],
                                                       avg_rent=query[3],
                                                       avg_supply=query[4]))
        return results

    def get_queryset_by_coordinates_range_dto(self, dto: CoordinatesRangeDto) -> Optional[list]:
        filters = list()
        filters.append(func.ST_Contains(func.ST_MakeEnvelope(dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326),
                                        RealEstateModel.coordinates))
        filters.append(or_(and_(RealEstateModel.is_available == "True",
                                PrivateSaleModel.is_available == "True",
                                func.to_date(PrivateSaleModel.contract_date, "YYYYMMDD") >= get_month_from_today(),
                                func.to_date(PrivateSaleModel.contract_date, "YYYYMMDD") <= get_server_timestamp()),
                           and_(RealEstateModel.is_available == "True",
                                PublicSaleModel.is_available == "True"),
                           and_(RealEstateModel.is_available == "True",
                                PrivateSaleModel.is_available == "True",
                                PublicSaleModel.is_available == "True",
                                func.to_date(PrivateSaleModel.contract_date, "YYYYMMDD") >= get_month_from_today(),
                                func.to_date(PrivateSaleModel.contract_date, "YYYYMMDD") <= get_server_timestamp())))

        query = (
            session.query(RealEstateModel,
                          func.avg(PrivateSaleModel.trade_price).label("avg_trade_price"),
                          func.avg(PrivateSaleModel.deposit_price)
                              .filter(PrivateSaleModel.trade_type == "전세").label("avg_deposit_price"),
                          func.avg(PrivateSaleModel.rent_price).label("avg_rent_price"),
                          func.avg(PublicSaleDetailModel.supply_price).label("avg_supply_price"),
                          )
                .join(RealEstateModel.private_sales, isouter=True)
                .join(RealEstateModel.public_sales, isouter=True)
                .join(PublicSaleModel.public_sale_details, isouter=True)
                .join(PublicSaleModel.public_sale_photos, isouter=True)
                .filter(*filters)
                .group_by(RealEstateModel.id)

        )

        queryset = query.all()

        return self._make_object_bounding_entity_from_queryset(queryset=queryset)

    def _make_bounding_administrative_entity_from_queryset(self, queryset: Optional[list]) -> Optional[list]:
        if not queryset:
            return None

        # Make Entity
        results = list()
        for query in queryset:
            results.append(query.to_entity())
        return results

    def get_administrative_queryset_by_coordinates_range_dto(self, dto: CoordinatesRangeDto) -> Optional[list]:
        """
             dto.level: 6 ~ 14
             <filter condition>
                11 이상 -> 읍, 면, 동, 리 (AdministrativeDivisionModel.level -> "3")
                9 ~ 11 -> 시, 군, 구 (AdministrativeDivisionModel.level -> "2")
                8 이하 -> 시, 도 (AdministrativeDivisionModel.level -> "1")
        """
        filters = list()
        filters.append(func.ST_Contains(func.ST_MakeEnvelope(dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326),
                                        AdministrativeDivisionModel.coordinates))

        if dto.level > 11:
            filters.append(AdministrativeDivisionModel.level == "3")
        elif 8 < dto.level < 12:
            filters.append(AdministrativeDivisionModel.level == "2")
        else:
            filters.append(AdministrativeDivisionModel.level == "1")

        query = session.query(AdministrativeDivisionModel).filter(*filters)
        queryset = query.all()

        return self._make_bounding_administrative_entity_from_queryset(queryset=queryset)
