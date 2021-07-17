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
from core.domains.house.dto.house_dto import CoordinatesRangeDto, GetHousePublicDetailDto
from sqlalchemy import exc
from app.extensions.utils.log_helper import logger_
from app.extensions.database import session
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.entity.house_entity import HousePublicDetailEntity
from core.domains.house.enum.house_enum import BoundingLevelEnum, BuildTypeEnum, RealTradeTypeEnum
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
                                                       avg_supply=query[4],
                                                       avg_private_pyoung=self._convert_supply_area_to_pyoung_number(
                                                           query[5]),
                                                       avg_public_pyoung=self._convert_supply_area_to_pyoung_number(
                                                           query[6])))

        return results

    def get_bounding_queryset_by_coordinates_range_dto(self, dto: CoordinatesRangeDto) -> Optional[list]:
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
                          func.avg(PrivateSaleModel.supply_area).label("avg_private_supply_area"),
                          func.avg(PublicSaleDetailModel.supply_area).label("avg_public_supply_area")
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
                12 ~ 14 -> 읍, 면, 동, 리 (AdministrativeDivisionModel.level -> "3")
                9 ~ 11 -> 시, 군, 구 (AdministrativeDivisionModel.level -> "2")
                8 이하 -> 시, 도 (AdministrativeDivisionModel.level -> "1")
        """
        filters = list()
        filters.append(func.ST_Contains(func.ST_MakeEnvelope(dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326),
                                        AdministrativeDivisionModel.coordinates))

        if dto.level > BoundingLevelEnum.MAX_SI_GUN_GU_LEVEL.value:
            filters.append(AdministrativeDivisionModel.level == "3")
        elif BoundingLevelEnum.MIN_SI_GUN_GU_LEVEL.value <= dto.level <= BoundingLevelEnum.MAX_SI_GUN_GU_LEVEL.value:
            filters.append(AdministrativeDivisionModel.level == "2")
        else:
            filters.append(AdministrativeDivisionModel.level == "1")

        query = session.query(AdministrativeDivisionModel).filter(*filters)
        queryset = query.all()

        return self._make_bounding_administrative_entity_from_queryset(queryset=queryset)

    def _convert_supply_area_to_pyoung_number(self, supply_area: Optional[float]) -> Optional[int]:
        """
            1평 = 3.3058 (제곱미터)
        """
        if supply_area:
            return round(supply_area / 3.3058)
        else:
            return None

    def has_public_sale_house(self, dto: GetHousePublicDetailDto) -> bool:
        house = session.query(RealEstateModel).filter_by(id=dto.house_id).first()

        if not house or not house.public_sales:
            return False
        return True

    def is_user_liked_house(self, interest_house: Optional[InterestHouseModel]) -> bool:
        if not interest_house:
            return False
        return interest_house.is_like

    def get_interest_house(self, dto: GetHousePublicDetailDto) -> Optional[InterestHouseModel]:
        filters = list()
        filters.append(InterestHouseModel.user_id == dto.user_id)
        filters.append(InterestHouseModel.house_id == dto.house_id)
        filters.append(InterestHouseModel.type == 1)

        interest_house = session.query(InterestHouseModel).filter(*filters).first()

        if not interest_house:
            return None
        return interest_house

    def _get_house_with_public_sales_by_id(self, house_id: int) -> list:
        """
            상세페이지로 보여줄 RealEstate 분양 매물
            - house_id -> has_public_sale_house()로부터 분양 매물인지 검증 받은 id 값
        """
        filters = list()
        filters.append(RealEstateModel.id == house_id)
        filters.append(and_(RealEstateModel.is_available == "True",
                            PublicSaleModel.is_available == "True"))
        query = (
            session.query(
                RealEstateModel,
                func.min(PublicSaleDetailModel.supply_area).label("min_supply_area"),
                func.max(PublicSaleDetailModel.supply_area).label("max_supply_area"),
                func.avg(PublicSaleDetailModel.supply_price).label("avg_supply_price"),
                func.avg(PublicSaleDetailModel.supply_area).label("avg_supply_area"),
                func.min(PublicSaleDetailModel.acquisition_tax).label("min_acquisition_tax"),
                func.max(PublicSaleDetailModel.acquisition_tax).label("max_acquisition_tax"),
            )
                .join(RealEstateModel.public_sales)
                .join(PublicSaleModel.public_sale_details)
                .join(PublicSaleModel.public_sale_photos)
                .filter(*filters)
                .group_by(RealEstateModel.id)
        )
        return query.first()

    def _make_house_with_private_entities_from_queryset(self, queryset: Optional[list]) -> Optional[list]:
        if not queryset:
            return None

        # Make Entity
        results = list()
        for query in queryset:
            results.append(query[0].to_estate_with_private_sales_entity(
                avg_trade=float(query[1]),
                avg_private_pyoung=self._convert_supply_area_to_pyoung_number(query[2])
            ))

        return results

    def _get_supply_price_per_pyoung(self,
                                     supply_price: Optional[float],
                                     avg_pyoung_number: Optional[float]) -> float:
        if not avg_pyoung_number or not supply_price:
            return 0
        return supply_price / avg_pyoung_number

    def _make_house_public_detail_entity_from_queryset(self, house_with_public_sales: list,
                                                       house_with_private_entities: Optional[list],
                                                       is_like: bool) -> HousePublicDetailEntity:
        return house_with_public_sales[0].to_house_with_public_detail_entity(
            is_like=is_like,
            min_pyoung_number=self._convert_supply_area_to_pyoung_number(house_with_public_sales[1]),
            max_pyoung_number=self._convert_supply_area_to_pyoung_number(house_with_public_sales[2]),
            min_supply_area=house_with_public_sales[1],
            max_supply_area=house_with_public_sales[2],
            avg_supply_price=house_with_public_sales[3],
            supply_price_per_pyoung=self._get_supply_price_per_pyoung(supply_price=float(house_with_public_sales[3]),
                                                                      avg_pyoung_number=house_with_public_sales[4]),
            min_acquisition_tax=house_with_public_sales[5],
            max_acquisition_tax=house_with_public_sales[6],
            near_houses=house_with_private_entities
        )

    def get_house_public_detail_queryset_by_get_house_public_detail_dto(self, dto: GetHousePublicDetailDto,
                                                                        degrees: float,
                                                                        is_like: bool) -> HousePublicDetailEntity:
        """
            <주변 실거래가 매물 List 가져오기>
            Postgis func- ST_DWithin(A_Geometry, B_Geometry, degrees) -> bool
            : A_Geometry 기준, 반경 x degree 이내 B_Geometry 속하면 True, or False
            -> A_Geometry : 분양 매물 위치
            -> B_Geometry : 주변 실거래가 매물
            -> degrees : 반경 1도 -> 약 111km (검색 결과에 따라 범위 조정 필요합니다.)

            <최종 Entity 구성>
            : 분양 매물 상세 queryset + is_like + 주변 실거래가 queryset -> HousePublicDetailEntity
        """
        # 분양 매물 상세 query -> house_with_public_sales
        house_with_public_sales = self._get_house_with_public_sales_by_id(house_id=dto.house_id)

        # 주변 실거래가 List queryset -> house_with_private_queryset
        filters = list()
        filters.append(func.ST_DWithin(house_with_public_sales[0].coordinates,
                                       RealEstateModel.coordinates,
                                       degrees))
        filters.append(and_(RealEstateModel.is_available == "True",
                            PrivateSaleModel.is_available == "True",
                            PrivateSaleModel.trade_type == RealTradeTypeEnum.TRADING.value,
                            PrivateSaleModel.building_type == BuildTypeEnum.APARTMENT.value,
                            func.to_date(PrivateSaleModel.contract_date, "YYYYMMDD") >= get_month_from_today(),
                            func.to_date(PrivateSaleModel.contract_date, "YYYYMMDD") <= get_server_timestamp()))

        query = (
            session.query(
                RealEstateModel,
                func.avg(PrivateSaleModel.trade_price).label("avg_trade_price"),
                func.avg(PrivateSaleModel.supply_area).label("avg_private_supply_area"),
            )
                .join(RealEstateModel.private_sales)
                .filter(*filters)
                .group_by(RealEstateModel.id)
        )

        house_with_private_queryset = query.all()
        house_with_private_entities = self._make_house_with_private_entities_from_queryset(
            queryset=house_with_private_queryset)

        return self._make_house_public_detail_entity_from_queryset(
            house_with_public_sales=house_with_public_sales,
            house_with_private_entities=house_with_private_entities,
            is_like=is_like
        )
