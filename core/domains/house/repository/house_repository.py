import datetime
from typing import Optional, List, Any

from geoalchemy2 import Geometry, func as geo_func
from sqlalchemy import and_, func, or_, literal, String, exists, union
from sqlalchemy import exc
from sqlalchemy.orm import joinedload, selectinload, contains_eager
from sqlalchemy.sql.functions import _FunctionGenerator

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.extensions.utils.query_helper import RawQueryHelper
from app.extensions.utils.time_helper import (
    get_month_from_today,
    get_server_timestamp,
    get_month_from_date,
)
from app.persistence.model import (
    RealEstateModel,
    PrivateSaleModel,
    PublicSaleModel,
    AdministrativeDivisionModel,
    PublicSaleDetailModel,
    InterestHouseModel,
    PrivateSaleDetailModel,
    RecentlyViewModel,
    PublicSalePhotoModel,
    PublicSaleAvgPriceModel,
    PrivateSaleAvgPriceModel,
)
from core.domains.banner.entity.banner_entity import ButtonLinkEntity
from core.domains.house.dto.house_dto import (
    CoordinatesRangeDto,
    GetHousePublicDetailDto,
    UpsertInterestHouseDto,
    GetSearchHouseListDto,
)
from core.domains.house.entity.house_entity import (
    HousePublicDetailEntity,
    RealEstateWithPrivateSaleEntity,
    AdministrativeDivisionEntity,
    BoundingRealEstateEntity,
    InterestHouseListEntity,
    GetRecentViewListEntity,
    GetSearchHouseListEntity,
    GetPublicSaleOfTicketUsageEntity,
    DetailCalendarInfoEntity,
    SimpleCalendarInfoEntity,
    PublicSaleReportEntity,
    PrivateSaleDetailEntity,
)
from core.domains.house.enum.house_enum import (
    BoundingLevelEnum,
    BuildTypeEnum,
    RealTradeTypeEnum,
    HouseTypeEnum,
    DivisionLevelEnum,
)
from core.domains.report.entity.report_entity import TicketUsageResultEntity
from core.domains.user.dto.user_dto import GetUserDto
from core.exceptions import NotUniqueErrorException, UpdateFailErrorException

logger = logger_.getLogger(__name__)


class HouseRepository:
    def create_interest_house(self, dto: UpsertInterestHouseDto) -> None:
        try:
            interest_house = InterestHouseModel(
                user_id=dto.user_id, house_id=dto.house_id, type=dto.type, is_like=True
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
            interest_house = (
                session.query(InterestHouseModel)
                .filter(*filters)
                .update({"is_like": dto.is_like, "updated_at": get_server_timestamp()})
            )
            session.commit()

            return interest_house
        except Exception as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][update_is_like_house] house_id : {dto.house_id} error : {e}"
            )

    def get_bounding_filter_with_two_points(
        self, dto: CoordinatesRangeDto
    ) -> _FunctionGenerator:
        return func.ST_Contains(
            func.ST_MakeEnvelope(dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326),
            RealEstateModel.coordinates,
        )

    def get_bounding_filter_with_radius(
        self, geometry_coordinates: Geometry, degree: float
    ) -> _FunctionGenerator:
        return func.ST_DWithin(
            geometry_coordinates, RealEstateModel.coordinates, degree,
        )

    def get_bounding(self, bounding_filter: Any) -> Optional[list]:
        filters = list()
        filters.append(bounding_filter)
        filters.append(RealEstateModel.is_available == "True",)

        query = (
            session.query(RealEstateModel,)
            .options(joinedload(RealEstateModel.private_sales))
            .options(joinedload("private_sales.private_sale_avg_prices"))
            .options(joinedload(RealEstateModel.public_sales))
            .options(joinedload("public_sales.public_sale_avg_prices"))
            .options(joinedload("public_sales.public_sale_photos"))
            .filter(*filters)
        )

        # RawQueryHelper.print_raw_query(query)
        queryset = query.all()

        if not queryset:
            return None

        return [query.to_bounding_entity() for query in queryset]

    def _make_bounding_administrative_entity(
        self, queryset: Optional[list]
    ) -> Optional[List[AdministrativeDivisionEntity]]:
        if not queryset:
            return None

        # Make Entity
        results = list()
        for query in queryset:
            results.append(query.to_entity())
        return results

    def get_administrative_divisions(self, dto: CoordinatesRangeDto) -> Optional[list]:
        """
             dto.level: 6 ~ 14
             <filter condition>
                12 ~ 14 -> 읍, 면, 동, 리 (AdministrativeDivisionModel.level -> "3")
                9 ~ 11 -> 시, 군, 구 (AdministrativeDivisionModel.level -> "2")
                8 이하 -> 시, 도 (AdministrativeDivisionModel.level -> "1")
        """
        filters = list()
        filters.append(
            func.ST_Contains(
                func.ST_MakeEnvelope(
                    dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326
                ),
                AdministrativeDivisionModel.coordinates,
            )
        )

        if dto.level > BoundingLevelEnum.MAX_SI_GUN_GU_LEVEL.value:
            filters.append(
                AdministrativeDivisionModel.level == DivisionLevelEnum.LEVEL_3.value
            )
        elif (
            BoundingLevelEnum.MIN_SI_GUN_GU_LEVEL.value
            <= dto.level
            <= BoundingLevelEnum.MAX_SI_GUN_GU_LEVEL.value
        ):
            filters.append(
                AdministrativeDivisionModel.level == DivisionLevelEnum.LEVEL_2.value
            )
        else:
            filters.append(
                AdministrativeDivisionModel.level == DivisionLevelEnum.LEVEL_1.value
            )

        query = session.query(AdministrativeDivisionModel).filter(*filters)
        queryset = query.all()

        return self._make_bounding_administrative_entity(queryset=queryset)

    def _convert_supply_area_to_pyoung_number(
        self, supply_area: Optional[float]
    ) -> Optional[int]:
        """
            1평 = 3.3058 (제곱미터)
        """
        if supply_area:
            return round(supply_area / 3.3058)
        else:
            return None

    def _is_enable_real_estate(self, real_estate_id: int) -> bool:
        real_estate = (
            session.query(RealEstateModel).filter_by(id=real_estate_id).first()
        )

        if not real_estate or real_estate.is_available == "False":
            return False
        return True

    def is_enable_public_sale_house(self, house_id: int) -> bool:
        house = session.query(PublicSaleModel).filter_by(id=house_id).first()

        if not house or house.is_available == "False":
            return False
        elif not self._is_enable_real_estate(house.real_estate_id):
            return False
        return True

    def is_user_liked_house(self, interest_house: Optional[InterestHouseModel]) -> bool:
        if not interest_house:
            return False
        return interest_house.is_like

    def get_public_interest_house(
        self, dto: GetHousePublicDetailDto
    ) -> Optional[InterestHouseModel]:
        filters = list()
        filters.append(InterestHouseModel.user_id == dto.user_id)
        filters.append(InterestHouseModel.house_id == dto.house_id)
        filters.append(InterestHouseModel.type == HouseTypeEnum.PUBLIC_SALES.value)

        interest_house = session.query(InterestHouseModel).filter(*filters).first()

        if not interest_house:
            return None
        return interest_house

    def get_house_with_public_sales(self, house_id: int) -> list:
        filters = list()
        filters.append(PublicSaleModel.id == house_id)
        filters.append(
            and_(
                RealEstateModel.is_available == "True",
                PublicSaleModel.is_available == "True",
            )
        )
        query = (
            session.query(
                RealEstateModel,
                func.min(PublicSaleDetailModel.supply_area).label("min_supply_area"),
                func.max(PublicSaleDetailModel.supply_area).label("max_supply_area"),
                func.avg(PublicSaleDetailModel.supply_price).label("avg_supply_price"),
                func.avg(PublicSaleDetailModel.supply_area).label("avg_supply_area"),
                func.min(PublicSaleDetailModel.acquisition_tax).label(
                    "min_acquisition_tax"
                ),
                func.max(PublicSaleDetailModel.acquisition_tax).label(
                    "max_acquisition_tax"
                ),
            )
            .join(RealEstateModel.public_sales)
            .join(PublicSaleModel.public_sale_details)
            .filter(*filters)
            .group_by(RealEstateModel.id)
        )
        return query.first()

    def _make_house_with_private_entities(
        self, queryset: Optional[list]
    ) -> Optional[List[RealEstateWithPrivateSaleEntity]]:
        if not queryset:
            return None

        # Make Entity
        # Slow Query Problem_2
        results = list()
        for query in queryset:
            results.append(
                query[0].to_estate_with_private_sales_entity(
                    avg_trade=float(query[1]),
                    avg_private_pyoung=self._convert_supply_area_to_pyoung_number(
                        query[2]
                    ),
                )
            )

        return results

    def _get_supply_price_per_pyoung(
        self, supply_price: Optional[float], avg_pyoung_number: Optional[float]
    ) -> float:
        if not avg_pyoung_number or not supply_price:
            return 0
        return supply_price / avg_pyoung_number

    def make_house_public_detail_entity(
        self,
        house_with_public_sales: list,
        is_like: bool,
        button_link_list: List[ButtonLinkEntity],
        ticket_usage_results: List[TicketUsageResultEntity],
    ) -> HousePublicDetailEntity:
        return house_with_public_sales[0].to_house_with_public_detail_entity(
            is_like=is_like,
            min_pyoung_number=self._convert_supply_area_to_pyoung_number(
                house_with_public_sales[1]
            ),
            max_pyoung_number=self._convert_supply_area_to_pyoung_number(
                house_with_public_sales[2]
            ),
            min_supply_area=house_with_public_sales[1],
            max_supply_area=house_with_public_sales[2],
            avg_supply_price=house_with_public_sales[3],
            supply_price_per_pyoung=self._get_supply_price_per_pyoung(
                supply_price=float(house_with_public_sales[3]),
                avg_pyoung_number=house_with_public_sales[4],
            ),
            min_acquisition_tax=house_with_public_sales[5],
            max_acquisition_tax=house_with_public_sales[6],
            button_links=button_link_list,
            ticket_usage_results=ticket_usage_results,
        )

    def get_public_with_private_sales_in_radius(
        self, house_with_public_sales: list, degree: float
    ) -> Optional[List[RealEstateWithPrivateSaleEntity]]:
        """
            <주변 실거래가 매물 List 가져오기>
            Postgis func- ST_DWithin(A_Geometry, B_Geometry, degree) -> bool
            : A_Geometry 기준, 반경 x degree 이내 B_Geometry 속하면 True, or False
            -> A_Geometry : 분양 매물 위치
            -> B_Geometry : 주변 실거래가 매물
            -> degree : 반경 1도 -> 약 111km (검색 결과에 따라 범위 조정 필요합니다.)

            <최종 Entity 구성>
            : 분양 매물 상세 queryset + is_like + 주변 실거래가 queryset -> HousePublicDetailEntity
        """

        if not house_with_public_sales:
            return None

        # 주변 실거래가 List queryset -> house_with_private_queryset
        filters = list()
        filters.append(
            geo_func.ST_DWithin(
                house_with_public_sales[0].coordinates,
                RealEstateModel.coordinates,
                degree,
            )
        )

        filters.append(
            and_(
                RealEstateModel.is_available == "True",
                PrivateSaleDetailModel.is_available == "True",
                PrivateSaleDetailModel.trade_type == RealTradeTypeEnum.TRADING.value,
                PrivateSaleModel.building_type == BuildTypeEnum.APARTMENT.value,
                PrivateSaleDetailModel.contract_date
                >= get_month_from_today().strftime("%Y%m%d"),
                PrivateSaleDetailModel.contract_date
                <= get_server_timestamp().strftime("%Y%m%d"),
            )
        )
        # Slow Query Problem_1
        query = (
            session.query(
                RealEstateModel,
                func.avg(PrivateSaleDetailModel.trade_price).label("avg_trade_price"),
                func.avg(PrivateSaleDetailModel.supply_area).label(
                    "avg_private_supply_area"
                ),
            )
            .join(
                PrivateSaleModel, RealEstateModel.id == PrivateSaleModel.real_estate_id
            )
            .join(
                PrivateSaleDetailModel,
                PrivateSaleModel.id == PrivateSaleDetailModel.private_sales_id,
            )
            .options(contains_eager(RealEstateModel.private_sales))
            .options(contains_eager("private_sales.private_sale_details"))
            .filter(*filters)
            .group_by(
                RealEstateModel.id, PrivateSaleModel.id, PrivateSaleDetailModel.id
            )
            .limit(10)
        )
        house_with_private_queryset = query.all()

        return self._make_house_with_private_entities(
            queryset=house_with_private_queryset
        )

    def _make_detail_calendar_info_entity(
        self, queryset: Optional[list], user_id: int
    ) -> List[DetailCalendarInfoEntity]:

        """
            <최종 Entity 구성>
            : 분양 매물 + 상세 queryset + is_like -> DetailCalendarInfoEntity
        """
        result = list()
        if queryset:
            for query in queryset:
                dto = GetHousePublicDetailDto(user_id=user_id, house_id=query.id)

                # 사용자가 해당 분양 매물에 대해 찜하기 했는지 여부
                is_like = self.is_user_liked_house(
                    self.get_public_interest_house(dto=dto)
                )
                result.append(query.to_detail_calendar_info_entity(is_like=is_like))

        return result

    def _make_simple_calendar_info_entity(
        self, queryset: Optional[list], user_id: int
    ) -> List[SimpleCalendarInfoEntity]:

        """
            <최종 Entity 구성>
            : 분양 매물 + 상세 queryset + is_like -> SimpleCalendarInfoEntity
        """
        result = list()

        if queryset:
            for query in queryset:
                # dto = GetHousePublicDetailDto(user_id=user_id, house_id=query.id)

                # 사용자가 해당 분양 매물에 대해 찜하기 했는지 여부
                # is_like = self.is_user_liked_house(
                #     self.get_public_interest_house(dto=dto)
                # )
                result.append(query.to_simple_calendar_info_entity(is_like=False))
        return result

    def get_calendar_info_filters(self, year_month: str) -> list:
        """
            year_month example - "202108"
        """
        filters = list()
        filters.append(
            and_(
                RealEstateModel.is_available == "True",
                PublicSaleModel.is_available == "True",
            )
        )

        filters.append(
            or_(
                PublicSaleModel.subscription_start_date.startswith(year_month),
                PublicSaleModel.subscription_end_date.startswith(year_month),
                PublicSaleModel.special_supply_date.startswith(year_month),
                PublicSaleModel.special_supply_etc_date.startswith(year_month),
                PublicSaleModel.first_supply_date.startswith(year_month),
                PublicSaleModel.first_supply_etc_date.startswith(year_month),
                PublicSaleModel.second_supply_date.startswith(year_month),
                PublicSaleModel.second_supply_etc_date.startswith(year_month),
                PublicSaleModel.notice_winner_date.startswith(year_month),
            )
        )
        return filters

    def _get_calendar_info_queryset(self, search_filters: list) -> Optional[list]:
        query = (
            session.query(RealEstateModel)
            .join(RealEstateModel.public_sales)
            .options(selectinload(RealEstateModel.public_sales))
            .filter(*search_filters)
        )
        queryset = query.all()

        return queryset

    def get_detail_calendar_info(
        self, user_id: int, search_filters: list
    ) -> List[DetailCalendarInfoEntity]:
        queryset = self._get_calendar_info_queryset(search_filters=search_filters)
        return self._make_detail_calendar_info_entity(
            queryset=queryset, user_id=user_id
        )

    def get_simple_calendar_info(
        self, user_id: int, search_filters: list
    ) -> List[SimpleCalendarInfoEntity]:
        queryset = self._get_calendar_info_queryset(search_filters=search_filters)
        return self._make_simple_calendar_info_entity(
            queryset=queryset, user_id=user_id
        )

    def get_interest_house_list(self, dto: GetUserDto) -> List[InterestHouseListEntity]:
        public_sales_query = (
            session.query(InterestHouseModel)
            .with_entities(
                InterestHouseModel.house_id,
                InterestHouseModel.type,
                PublicSaleModel.name,
                RealEstateModel.jibun_address,
                PublicSaleModel.subscription_start_date,
                PublicSaleModel.subscription_end_date,
                PublicSalePhotoModel.path.label("image_path"),
            )
            .join(
                PublicSaleModel,
                (InterestHouseModel.house_id == PublicSaleModel.id)
                & (InterestHouseModel.type == HouseTypeEnum.PUBLIC_SALES.value)
                & (InterestHouseModel.user_id == dto.user_id)
                & (InterestHouseModel.is_like == True),
            )
            .join(PublicSaleModel.real_estates)
            .join(PublicSaleModel.public_sale_photos, isouter=True)
        )

        private_sales_query = (
            session.query(InterestHouseModel)
            .with_entities(
                InterestHouseModel.house_id,
                InterestHouseModel.type,
                PrivateSaleModel.name,
                RealEstateModel.jibun_address,
                literal("", String).label("subscription_start_date"),
                literal("", String).label("subscription_end_date"),
                literal("", String).label("image_path"),
            )
            .join(
                PrivateSaleModel,
                (InterestHouseModel.house_id == PrivateSaleModel.id)
                & (InterestHouseModel.type == HouseTypeEnum.PRIVATE_SALES.value)
                & (InterestHouseModel.user_id == dto.user_id)
                & (InterestHouseModel.is_like == True),
            )
            .join(PrivateSaleModel.real_estates)
        )

        query = public_sales_query.union_all(private_sales_query)
        queryset = query.all()

        return self._make_interest_house_list_entity(queryset=queryset)

    def _make_interest_house_list_entity(
        self, queryset: Optional[List]
    ) -> List[InterestHouseListEntity]:

        result = list()

        if queryset:
            for query in queryset:
                result.append(
                    InterestHouseListEntity(
                        house_id=query.house_id,
                        type=query.type,
                        name=query.name,
                        jibun_address=query.jibun_address,
                        subscription_start_date=query.subscription_start_date,
                        subscription_end_date=query.subscription_end_date,
                        image_path=query.image_path,
                    )
                )

        return result

    def get_interest_house(
        self, user_id: int, house_id: int
    ) -> Optional[InterestHouseListEntity]:
        query = (
            session.query(InterestHouseModel)
            .with_entities(
                InterestHouseModel.house_id,
                InterestHouseModel.type,
                PublicSaleModel.name,
                RealEstateModel.jibun_address,
                PublicSaleModel.subscription_start_date,
                PublicSaleModel.subscription_end_date,
                PublicSalePhotoModel.path.label("image_path"),
            )
            .join(
                PublicSaleModel,
                (InterestHouseModel.house_id == PublicSaleModel.id)
                & (InterestHouseModel.type == HouseTypeEnum.PUBLIC_SALES.value)
                & (InterestHouseModel.user_id == user_id)
                & (InterestHouseModel.house_id == house_id),
            )
            .join(PublicSaleModel.real_estates)
            .join(PublicSaleModel.public_sale_photos, isouter=True)
        )

        queryset = query.first()

        if not queryset:
            return None

        return self._make_interest_house_entity(queryset=queryset)

    def _make_interest_house_entity(
        self, queryset: InterestHouseModel
    ) -> InterestHouseListEntity:
        return InterestHouseListEntity(
            house_id=queryset.house_id,
            type=queryset.type,
            name=queryset.name,
            jibun_address=queryset.jibun_address,
            subscription_start_date=queryset.subscription_start_date,
            subscription_end_date=queryset.subscription_end_date,
        )

    def get_recent_view_list(self, dto: GetUserDto) -> List[GetRecentViewListEntity]:
        # private_sales 는 X -> MVP 에서는 매매 상세화면이 없음
        query = (
            session.query(RecentlyViewModel)
            .with_entities(
                RecentlyViewModel.house_id,
                RecentlyViewModel.type,
                PublicSaleModel.name,
                PublicSalePhotoModel.path,
            )
            .join(
                PublicSaleModel,
                (RecentlyViewModel.house_id == PublicSaleModel.id)
                & (RecentlyViewModel.type == HouseTypeEnum.PUBLIC_SALES.value)
                & (RecentlyViewModel.user_id == dto.user_id),
            )
            .join(PublicSaleModel.public_sale_photos, isouter=True)
        )

        queryset = query.all()
        return self._make_get_recent_view_list_entity(queryset=queryset)

    def _make_get_recent_view_list_entity(
        self, queryset: Optional[List]
    ) -> List[GetRecentViewListEntity]:
        result = list()

        if queryset:
            for query in queryset:
                result.append(
                    GetRecentViewListEntity(
                        house_id=query.house_id,
                        type=query.type,
                        name=query.name,
                        image_path=query.path,
                    )
                )

        return result

    def _make_get_search_house_list_entity(
        self, queryset: Optional[List], user_id: int
    ) -> List[GetSearchHouseListEntity]:
        search_entities = list()

        if queryset:
            for query in queryset:
                is_like = self.is_user_liked_house(
                    self.get_public_interest_house(
                        dto=GetHousePublicDetailDto(user_id=user_id, house_id=query.id)
                    )
                )
                is_receiving = self._is_subscription_receiving(
                    start_date=query.subscription_start_date,
                    end_date=query.subscription_end_date,
                )
                avg_down_payment = self._get_avg_down_payment(
                    min_down_payment=query.min_down_payment,
                    max_down_payment=query.max_down_payment,
                )
                # avg_supply_price =
                search_entities.append(
                    GetSearchHouseListEntity(
                        house_id=query.id,
                        name=query.name,
                        jibun_address=query.jibun_address,
                        is_like=is_like,
                        image_path=query.path,
                        subscription_start_date=query.subscription_start_date,
                        subscription_end_date=query.subscription_end_date,
                        is_receiving=is_receiving,
                        avg_down_payment=avg_down_payment,
                        avg_supply_price=query.avg_supply_price
                        if query.avg_supply_price
                        else 0,
                    )
                )

        return search_entities

    def get_search_house_list(
        self, dto: GetSearchHouseListDto
    ) -> List[GetSearchHouseListEntity]:
        """
            todo: 검색 성능 고도화 필요
            - full_scan 방식
            - %LIKE% : 서로 다른 두 단어부터 검색 불가
            - Full Text Search 필요(ts_vector, pg_trgm, elastic_search...)
        """
        filters = list()
        filters.append(
            and_(
                RealEstateModel.is_available == "True",
                RealEstateModel.jibun_address.contains(dto.keywords),
                PublicSaleModel.is_available == "True",
            )
        )

        query = (
            session.query(PublicSaleModel)
            .with_entities(
                PublicSaleModel.id,
                PublicSaleModel.name,
                RealEstateModel.jibun_address,
                PublicSaleModel.subscription_start_date,
                PublicSaleModel.subscription_end_date,
                PublicSaleModel.min_down_payment,
                PublicSaleModel.max_down_payment,
                PublicSalePhotoModel.path,
                func.avg(PublicSaleAvgPriceModel.supply_price).label(
                    "avg_supply_price"
                ),
            )
            .join(PublicSaleModel.real_estates)
            .join(PublicSaleModel.public_sale_photos, isouter=True)
            .join(PublicSaleModel.public_sale_avg_prices)
            .filter(*filters)
            .group_by(PublicSaleModel.id, RealEstateModel.id, PublicSalePhotoModel.id)
        )

        queryset = query.all()

        return self._make_get_search_house_list_entity(
            queryset=queryset, user_id=dto.user_id,
        )

    def get_geometry_coordinates_from_real_estate(
        self, real_estate_id: int
    ) -> Optional[Geometry]:
        real_estate = (
            session.query(RealEstateModel).filter_by(id=real_estate_id).first()
        )

        if real_estate:
            return real_estate.coordinates
        return None

    def get_geometry_coordinates_from_public_sale(
        self, public_sale_id: int
    ) -> Optional[Geometry]:
        public_sale = (
            session.query(PublicSaleModel).filter_by(id=public_sale_id).first()
        )

        if public_sale:
            return self.get_geometry_coordinates_from_real_estate(
                real_estate_id=public_sale.real_estate_id
            )
        return None

    def get_geometry_coordinates_from_administrative_division(
        self, administrative_division_id: int
    ) -> Optional[Geometry]:
        division = (
            session.query(AdministrativeDivisionModel)
            .filter_by(id=administrative_division_id)
            .first()
        )

        if division:
            return division.coordinates
        return None

    def get_public_sales_of_ticket_usage(
        self, public_house_ids: int
    ) -> List[GetPublicSaleOfTicketUsageEntity]:
        query = (
            session.query(PublicSaleModel)
            .options(joinedload(PublicSaleModel.public_sale_photos))
            .filter(PublicSaleModel.id.in_(public_house_ids))
        )

        query_set = query.all()
        return self._make_get_ticket_usage_result_entity(query_set=query_set)

    def _make_get_ticket_usage_result_entity(
        self, query_set: Optional[List]
    ) -> List[GetPublicSaleOfTicketUsageEntity]:
        result = list()

        if query_set:
            for query in query_set:
                result.append(
                    GetPublicSaleOfTicketUsageEntity(
                        house_id=query.id,
                        name=query.name,
                        image_path=query.public_sale_photos.path
                        if query.public_sale_photos
                        else None,
                    )
                )
        return result

    def get_public_sale_info(self, house_id: int) -> PublicSaleReportEntity:
        query = (
            session.query(PublicSaleModel)
            .options(joinedload(PublicSaleModel.real_estates, innerjoin=True))
            .options(joinedload(PublicSaleModel.public_sale_details, innerjoin=True))
            .options(joinedload(PublicSaleModel.public_sale_photos))
            .options(joinedload("public_sale_details.public_sale_detail_photos"))
            .options(joinedload("public_sale_details.public_sale_detail_photos"))
            .options(joinedload("public_sale_details.special_supply_results"))
            .options(joinedload("public_sale_details.general_supply_results"))
            .filter(PublicSaleModel.id == house_id)
        )
        query_set = query.first()
        return query_set.to_report_entity()

    def get_recently_public_sale_info(self, si_gun_gu: str) -> PublicSaleReportEntity:
        filters = list()
        filters.append(RealEstateModel.si_gun_gu == si_gun_gu)
        filters.append(
            PublicSaleModel.subscription_end_date
            < get_server_timestamp().strftime("%y%m%d")
        )
        query = (
            session.query(PublicSaleModel)
            .join(
                RealEstateModel,
                (RealEstateModel.id == PublicSaleModel.real_estate_id)
                & (RealEstateModel.si_gun_gu == si_gun_gu),
            )
            .options(contains_eager(PublicSaleModel.real_estates))
            .options(joinedload(PublicSaleModel.public_sale_details, innerjoin=True))
            .options(joinedload("public_sale_details.public_sale_detail_photos"))
            .options(joinedload("public_sale_details.special_supply_results"))
            .options(joinedload("public_sale_details.general_supply_results"))
            .options(joinedload(PublicSaleModel.public_sale_photos))
            .filter(*filters)
            .order_by(PublicSaleModel.subscription_end_date.desc())
            .limit(1)
        )

        query_set = query.first()
        return query_set.to_report_entity()

    def _is_subscription_receiving(
        self, start_date: Optional[str], end_date: Optional[str]
    ) -> bool:
        if not start_date or end_date:
            return False
        today = get_server_timestamp()
        start_date_to_datetime = datetime.datetime.strptime(start_date, "%Y%m%d")
        end_date_to_datetime = datetime.datetime.strptime(end_date, "%Y%m%d")
        if start_date_to_datetime <= today <= end_date_to_datetime:
            return True
        return False

    def _get_avg_down_payment(
        self, min_down_payment: Optional[int], max_down_payment: Optional[int]
    ) -> float:
        if not min_down_payment or max_down_payment:
            return 0
        return (min_down_payment + max_down_payment) / 2

    def get_recently_contracted_private_sale_details(
        self, private_sales_id: int
    ) -> PrivateSaleDetailEntity:
        filters = list()
        filters.append(
            and_(
                PrivateSaleDetailModel.private_sales_id == private_sales_id,
                PrivateSaleDetailModel.contract_date
                < get_server_timestamp().strftime("%y%m%d"),
            )
        )
        query = (
            session.query(PrivateSaleDetailModel)
            .filter(*filters)
            .order_by(PrivateSaleDetailModel.contract_date.desc())
            .limit(1)
        )
        result = query.first()

        return result.to_entity()

    def get_pre_calc_avg_date_filters(self, date_from: str) -> list:
        """
            date_from example: 20210915
            date_filters : date_from 로부터 1달 전 범위
        """
        date_filters = list()

        date_filters.append(
            and_(
                PrivateSaleDetailModel.contract_date
                >= get_month_from_date(date_from).strftime("%Y%m%d"),
                PrivateSaleDetailModel.contract_date <= date_from,
            )
        )

        return date_filters

    def get_pre_calc_avg_trade_price_target_of_private_sales(
        self, private_sales_id: int, date_filters: list
    ) -> list:
        filters = list()
        filters.append(
            and_(
                PrivateSaleDetailModel.private_sales_id == private_sales_id,
                PrivateSaleDetailModel.trade_type == "매매",
                PrivateSaleDetailModel.is_available == True,
            )
        )
        query = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.supply_area,
                func.avg(PrivateSaleDetailModel.trade_price).label("avg_trade_price"),
            )
            .filter(*date_filters, *filters)
            .group_by(PrivateSaleDetailModel.private_area)
        )
        # row : (supply_area, avg_deposit_price)
        return query.all()

    def get_pre_calc_avg_deposit_price_target_of_private_sales(
        self, private_sales_id: int, date_filters: list
    ) -> list:
        filters = list()
        filters.append(
            and_(
                PrivateSaleDetailModel.private_sales_id == private_sales_id,
                PrivateSaleDetailModel.trade_type == "전세",
                PrivateSaleDetailModel.is_available == True,
            )
        )
        query = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.supply_area,
                func.avg(PrivateSaleDetailModel.deposit_price).label(
                    "avg_deposit_price"
                ),
            )
            .filter(*date_filters, *filters)
            .group_by(PrivateSaleDetailModel.private_area)
        )
        # row : (supply_area, avg_deposit_price)
        return query.all()

    def _create_private_sale_avg_prices(
        self,
        private_sales_id: int,
        pyoung_number: int,
        default_pyoung: int,
        avg_trade_price: float = 0,
        avg_deposit_price: float = 0,
    ) -> None:

        try:
            instance = PrivateSaleAvgPriceModel(
                private_sales_id=private_sales_id,
                pyoung=pyoung_number,
                default_pyoung=default_pyoung,
                trade_price=avg_trade_price,
                deposit_price=avg_deposit_price,
            )

            session.add(instance)
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][create_private_sale_avg_trade_price] "
                f"private_sales_id : {private_sales_id} error : {e}"
            )
            raise NotUniqueErrorException

    def _update_private_sale_avg_trade_price(
        self, private_sales_id: int, pyoung_number: int, avg_trade_price: float
    ):
        try:

            session.query(PrivateSaleAvgPriceModel).filter_by(
                private_sales_id=private_sales_id
            ).update(
                {
                    "pyoung": pyoung_number,
                    "trade_price": avg_trade_price,
                    "updated_at": get_server_timestamp(),
                }
            )

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][update_private_sale_avg_trade_price] "
                f"private_sales_id : {private_sales_id} error : {e}"
            )
            raise UpdateFailErrorException

    def _is_exists_private_sale_avg_prices(
        self, private_sales_id: int, pyoung_number: int
    ) -> bool:
        query = session.query(
            exists().where(
                PrivateSaleAvgPriceModel.private_sales_id == private_sales_id,
                PrivateSaleAvgPriceModel.pyoung == pyoung_number,
            )
        )
        if query.scalar():
            return True
        return False

    def get_default_pyoung_number(
        self, private_sales_id: int, date_filters: list
    ) -> int:
        filters = list()
        filters.append(
            and_(
                PrivateSaleDetailModel.private_sales_id == private_sales_id,
                PrivateSaleDetailModel.is_available == True,
            )
        )
        query = (
            session.query(PrivateSaleDetailModel)
            .filter(*date_filters, *filters)
            .group_by(PrivateSaleDetailModel.id, PrivateSaleDetailModel.private_area)
            .count()
        )

        return query.all()

    def create_or_update_private_sale_avg_trade_prices(
        self, private_sales_id: int, trade_price_info: List[tuple]
    ):
        try:
            for elm in trade_price_info:
                pyoung = self._convert_supply_area_to_pyoung_number(supply_area=elm[0])
                # 이미 private_sale_avg_prices 테이블이 존재하면 업데이트, 없으면 새 Row 생성
                if self._is_exists_private_sale_avg_prices(
                    private_sales_id=private_sales_id, pyoung_number=pyoung
                ):
                    self._update_private_sale_avg_trade_price(
                        private_sales_id=private_sales_id,
                        pyoung_number=pyoung,
                        avg_trade_price=elm[1],
                    )
                else:
                    # todo: default pyoung_number 선정

                    self._create_private_sale_avg_prices(
                        private_sales_id=private_sales_id,
                        pyoung_number=pyoung,
                        default_pyoung=pyoung,
                        avg_trade_price=elm[1],
                    )
        except Exception as e:
            logger.error(
                f"[HouseRepository][create_or_update_private_sale_avg_prices] "
                f"private_sales_id : {private_sales_id} error : {e}"
            )
