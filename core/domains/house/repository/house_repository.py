from math import ceil
from typing import Optional, List, Any, Tuple

from geoalchemy2 import Geometry, func as geo_func
from sqlalchemy import and_, func, or_, literal, String, exists, Integer
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
    InterestHouseListEntity,
    GetRecentViewListEntity,
    GetSearchHouseListEntity,
    GetPublicSaleOfTicketUsageEntity,
    AdministrativeDivisionEntity,
    RealEstateWithPrivateSaleEntity,
    HousePublicDetailEntity,
    DetailCalendarInfoEntity,
    SimpleCalendarInfoEntity,
    PublicSaleReportEntity,
    RecentlyContractedEntity,
)
from core.domains.house.enum.house_enum import (
    BoundingLevelEnum,
    BuildTypeEnum,
    RealTradeTypeEnum,
    HouseTypeEnum,
    DivisionLevelEnum,
    PublicSaleStatusEnum,
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
        filters.append(
            and_(
                RealEstateModel.is_available == "True",
                # PrivateSaleModel.building_type != BuildTypeEnum.ROW_HOUSE.value
            )
        )

        # .join(RealEstateModel.private_sales, isouter=True)
        # .options(contains_eager(RealEstateModel.private_sales))
        query = (
            session.query(RealEstateModel,)
            .options(joinedload(RealEstateModel.private_sales))
            .options(joinedload(RealEstateModel.public_sales))
            .options(joinedload("private_sales.private_sale_avg_prices"))
            .options(joinedload("public_sales.public_sale_avg_prices"))
            .options(joinedload("public_sales.public_sale_photos"))
            .filter(*filters)
        )
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
             dto.level: 8 ~ 15
             <filter condition>
                13 ~ 15 -> 읍, 면, 동, 리 (AdministrativeDivisionModel.level -> "3")
                11 ~ 12 -> 시, 군, 구 (AdministrativeDivisionModel.level -> "2")
                8 ~ 10  -> 시, 도 (AdministrativeDivisionModel.level -> "1")
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
        filters.append(
            and_(
                RealEstateModel.is_available == "True",
                PublicSaleModel.is_available == "True",
                PublicSaleModel.id == house_id,
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

    def _get_status(
        self, subscription_start_date: str, subscription_end_date: str
    ) -> [int]:
        if (
            not subscription_start_date
            or subscription_start_date == "0"
            or subscription_start_date == "00000000"
            or not subscription_end_date
            or subscription_end_date == "0"
            or subscription_end_date == "00000000"
        ):
            return PublicSaleStatusEnum.UNKNOWN.value

        today = get_server_timestamp().strftime("%Y%m%d")

        if today < subscription_start_date:
            return PublicSaleStatusEnum.BEFORE_OPEN.value
        elif subscription_start_date <= today <= subscription_end_date:
            return PublicSaleStatusEnum.IS_RECEIVING.value
        elif subscription_end_date < today:
            return PublicSaleStatusEnum.IS_CLOSED.value
        else:
            return PublicSaleStatusEnum.UNKNOWN.value

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
                        status=self._get_status(
                            subscription_start_date=query.subscription_start_date,
                            subscription_end_date=query.subscription_end_date,
                        ),
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

    def _get_avg_down_payment(
        self, min_down_payment: Optional[int], max_down_payment: Optional[int]
    ) -> float:
        if not min_down_payment or max_down_payment:
            return 0
        return (min_down_payment + max_down_payment) / 2

    def get_recently_contracted_private_sale_details(
        self, private_sales_ids: List[int]
    ) -> List[RecentlyContractedEntity]:
        filters = list()
        filters.append(
            and_(PrivateSaleDetailModel.private_sales_id.in_(private_sales_ids),)
        )
        # todo. 추후 배치 돌릴시에는 한달 검색 조건 추가 필요
        query_cond1 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                func.max(PrivateSaleDetailModel.contract_date).label(
                    "sale_contract_date"
                ),
                literal("", String).label("rent_contract_date"),
                func.max(PrivateSaleAvgPriceModel.id).label(
                    "private_sale_avg_price_id"
                ),
            )
            .join(
                PrivateSaleAvgPriceModel,
                (
                    PrivateSaleDetailModel.private_sales_id
                    == PrivateSaleAvgPriceModel.private_sales_id
                )
                & (
                    func.ceil((PrivateSaleDetailModel.private_area * 1.35) / 3.3058)
                    == PrivateSaleAvgPriceModel.pyoung
                ),
                isouter=True,
            )
            .filter(*filters)
            .filter(PrivateSaleDetailModel.trade_type == "매매")
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.trade_type,
            )
        )

        query_cond2 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                literal("", String).label("sale_contract_date"),
                func.max(PrivateSaleDetailModel.contract_date).label(
                    "rent_contract_date"
                ),
                func.max(PrivateSaleAvgPriceModel.id).label(
                    "private_sale_avg_price_id"
                ),
            )
            .join(
                PrivateSaleAvgPriceModel,
                (
                    PrivateSaleDetailModel.private_sales_id
                    == PrivateSaleAvgPriceModel.private_sales_id
                )
                & (
                    func.ceil((PrivateSaleDetailModel.private_area * 1.35) / 3.3058)
                    == PrivateSaleAvgPriceModel.pyoung
                ),
                isouter=True,
            )
            .filter(*filters)
            .filter(PrivateSaleDetailModel.trade_type == "전세")
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.trade_type,
            )
        )

        union_query = query_cond1.union_all(query_cond2).subquery()

        query = session.query(
            func.max(union_query.columns.private_sale_details_private_sales_id).label(
                "private_sales_id"
            ),
            union_query.columns.private_sale_details_private_area.label("private_area"),
            func.max(union_query.columns.sale_contract_date).label(
                "sale_contract_date"
            ),
            func.max(union_query.columns.rent_contract_date).label(
                "rent_contract_date"
            ),
            func.max(union_query.columns.private_sale_avg_price_id).label(
                "private_sale_avg_price_id"
            ),
        ).group_by(
            union_query.columns.private_sale_details_private_area,
            union_query.columns.private_sale_details_private_sales_id,
        )

        query_set = query.all()

        RawQueryHelper.print_raw_query(query)

        if not query_set:
            return []

        return [
            RecentlyContractedEntity(
                private_sales_id=query[0],
                private_area=query[1],
                sale_contract_date=query[2],
                rent_contract_date=query[3],
                private_sale_avg_price_id=query[4],
            )
            for query in query_set
        ]

    def get_pre_calc_avg_prices_target_of_private_sales(
        self, recent_info: RecentlyContractedEntity
    ) -> List[Tuple]:
        """
            date_from example: 20210915
            date_filters : date_from 로부터 1달 전 범위
        """
        default_filters = list()
        sale_date_filters = list()
        rent_date_filters = list()

        default_filters.append(
            and_(
                PrivateSaleDetailModel.private_sales_id == recent_info.private_sales_id,
                PrivateSaleDetailModel.is_available == True,
                PrivateSaleDetailModel.private_area == recent_info.private_area,
            )
        )

        sale_contract_date = (
            recent_info.sale_contract_date
            if recent_info.sale_contract_date
            else recent_info.rent_contract_date
        )
        sale_date_filters.append(
            and_(
                PrivateSaleDetailModel.contract_date
                >= get_month_from_date(sale_contract_date).strftime("%Y%m%d"),
                PrivateSaleDetailModel.contract_date <= sale_contract_date,
            )
        )

        rent_contract_date = (
            recent_info.rent_contract_date
            if recent_info.rent_contract_date
            else recent_info.sale_contract_date
        )
        rent_date_filters.append(
            and_(
                PrivateSaleDetailModel.contract_date
                >= get_month_from_date(rent_contract_date).strftime("%Y%m%d"),
                PrivateSaleDetailModel.contract_date <= rent_contract_date,
            )
        )

        query_cond1 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_area,
                func.avg(PrivateSaleDetailModel.trade_price).label("avg_trade_price"),
                literal(0, Integer).label("avg_deposit_price"),
            )
            .filter(
                *sale_date_filters,
                *default_filters,
                PrivateSaleDetailModel.trade_type == "매매",
            )
            .group_by(PrivateSaleDetailModel.private_area)
        )

        query_cond2 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_area,
                literal(0, Integer).label("avg_trade_price"),
                func.avg(PrivateSaleDetailModel.deposit_price).label(
                    "avg_deposit_price"
                ),
            )
            .filter(
                *rent_date_filters,
                *default_filters,
                PrivateSaleDetailModel.trade_type == "전세",
            )
            .group_by(PrivateSaleDetailModel.private_area)
        )

        union_query = query_cond1.union_all(query_cond2).subquery()

        query = session.query(
            union_query.columns.private_sale_details_private_area.label("private_area"),
            func.max(union_query.columns.avg_trade_price).label("avg_trade_prices"),
            func.max(union_query.columns.avg_deposit_price).label("avg_deposit_prices"),
        ).group_by(union_query.columns.private_sale_details_private_area)

        # RawQueryHelper.print_raw_query(query)

        # row: (private_area, avg_trade_prices, avg_deposit_prices)
        return query.all()

    def make_pre_calc_target_private_sale_avg_prices_list(
        self,
        private_sales_id: int,
        query_set: List[Tuple],
        default_pyoung: int,
        private_sale_avg_price_id: Optional[int],
    ) -> Optional[Tuple[List[dict], List[dict]]]:
        if not query_set:
            return None
        avg_prices_update_list = list()
        avg_prices_create_list = list()

        # query_set : [(private_area, avg_trade_prices, avg_deposit_prices), ...]
        for query in query_set:
            avg_price_info = {
                "private_sales_id": private_sales_id,
                "pyoung": ceil(query[0] * 1.35 / 3.3058),  # todo. 공급면적 들어오기 전까지 사용 수식
                # "pyoung": self._convert_supply_area_to_pyoung_number(
                #     supply_area=query[0]
                # ),
                "default_pyoung": default_pyoung,
                "trade_price": query[1],
                "deposit_price": query[2],
                "id": private_sale_avg_price_id,
            }

            # if self._is_exists_private_sale_avg_prices(
            #         private_sales_id=avg_price_info["private_sales_id"],
            #         pyoung_number=avg_price_info["pyoung"],
            # ):
            if private_sale_avg_price_id:
                avg_price_info.update({"updated_at": get_server_timestamp()})
                avg_prices_update_list.append(avg_price_info)
            else:
                avg_prices_create_list.append(avg_price_info)

        return avg_prices_update_list, avg_prices_create_list

    def create_private_sale_avg_prices(self, create_list: List[dict]) -> None:
        try:
            session.bulk_insert_mappings(
                PrivateSaleAvgPriceModel, [create_info for create_info in create_list]
            )

            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][create_private_sale_avg_prices] error : {e}"
            )
            raise NotUniqueErrorException

    def update_private_sale_avg_prices(self, update_list: List[dict]) -> None:
        try:
            session.bulk_update_mappings(
                PrivateSaleAvgPriceModel, [update_info for update_info in update_list]
            )

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][update_private_sale_avg_prices] error : {e}"
            )
            raise UpdateFailErrorException

    def _is_exists_private_sale_avg_prices(
        self, private_sales_id: int, pyoung_number: int
    ) -> bool:
        query = session.query(
            exists().where(
                and_(
                    PrivateSaleAvgPriceModel.private_sales_id == private_sales_id,
                    PrivateSaleAvgPriceModel.pyoung == pyoung_number,
                )
            )
        )
        if query.scalar():
            return True
        return False

    def get_default_pyoung_number_for_private_sale(
        self, recent_info: RecentlyContractedEntity
    ) -> int:
        default_filters = list()

        default_filters.append(
            and_(
                PrivateSaleDetailModel.private_sales_id == recent_info.private_sales_id,
                PrivateSaleDetailModel.is_available == True,
            )
        )

        query = (
            session.query(
                PrivateSaleDetailModel.private_area,
                func.count(PrivateSaleDetailModel.private_area).label("count"),
            )
            .filter(*default_filters)
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
            )
            .order_by(
                func.count(PrivateSaleDetailModel.private_area).desc(),
                PrivateSaleDetailModel.private_area.asc(),
            )
            .limit(1)
        )

        # query_set: [(private_area, max(count))]
        query_set = query.all()

        # RawQueryHelper.print_raw_query(query)

        # todo. 공급면적 들어오기 전까지 사용 수식
        return ceil(query_set[0][0] * 1.35 / 3.3058)

        # return self._convert_supply_area_to_pyoung_number(
        #     supply_area=query_set[0][0] if query_set else 0
        # )

    def get_pre_calc_avg_prices_target_of_public_sales(
        self, public_sales_id: int
    ) -> List[Tuple]:
        query = (
            session.query(
                PublicSaleDetailModel.supply_area,
                func.avg(PublicSaleDetailModel.supply_price).label("avg_supply_price"),
            )
            .filter(PublicSaleDetailModel.public_sales_id == public_sales_id)
            .group_by(PublicSaleDetailModel.supply_area)
        )
        # query_set: [(supply_area, avg_supply_price)]
        return query.all()

    def get_default_pyoung_number_for_public_sale(self, public_sales_id: int) -> int:
        query = (
            session.query(
                PublicSaleDetailModel.supply_area,
                func.count(PublicSaleDetailModel.supply_area).label("count"),
            )
            .filter(PublicSaleDetailModel.public_sales_id == public_sales_id)
            .group_by(
                PublicSaleDetailModel.public_sales_id,
                PublicSaleDetailModel.supply_area,
            )
            .order_by(
                func.count(PublicSaleDetailModel.supply_area).desc(),
                PublicSaleDetailModel.supply_area.asc(),
            )
            .limit(1)
        )
        # query_set: [(supply_area, max(count))]
        query_set = query.all()

        return self._convert_supply_area_to_pyoung_number(
            supply_area=query_set[0][0] if query_set else 0
        )

    def _is_exists_public_sale_avg_prices(
        self, public_sales_id: int, pyoung_number: int
    ) -> bool:
        query = session.query(
            exists().where(
                and_(
                    PublicSaleAvgPriceModel.public_sales_id == public_sales_id,
                    PublicSaleAvgPriceModel.pyoung == pyoung_number,
                )
            )
        )
        if query.scalar():
            return True
        return False

    def make_pre_calc_target_public_sale_avg_prices_list(
        self, public_sales_id: int, query_set: List[Tuple], default_pyoung: int
    ) -> Optional[Tuple[List[dict], List[dict]]]:
        if not query_set:
            return None
        avg_prices_update_list = list()
        avg_prices_create_list = list()

        # query_set : [(supply_area, avg_supply_prices), ...]
        for query in query_set:
            avg_price_info = {
                "public_sales_id": public_sales_id,
                "pyoung": self._convert_supply_area_to_pyoung_number(
                    supply_area=query[0]
                ),
                "default_pyoung": default_pyoung,
                "supply_price": query[1],
            }
            if self._is_exists_public_sale_avg_prices(
                public_sales_id=avg_price_info["public_sales_id"],
                pyoung_number=avg_price_info["pyoung"],
            ):
                avg_price_info.update({"updated_at": get_server_timestamp()})
                avg_prices_update_list.append(avg_price_info)
            else:
                avg_prices_create_list.append(avg_price_info)

        return avg_prices_update_list, avg_prices_create_list

    def update_public_sale_avg_prices(self, update_list: List[dict]) -> None:
        try:
            session.bulk_update_mappings(
                PublicSaleAvgPriceModel, [update_info for update_info in update_list]
            )

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][update_public_sale_avg_prices] error : {e}"
            )
            raise UpdateFailErrorException

    def create_public_sale_avg_prices(self, create_list: List[dict]) -> None:
        try:
            session.bulk_insert_mappings(
                PublicSaleAvgPriceModel, [create_info for create_info in create_list]
            )

            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][create_public_sale_avg_prices] error : {e}"
            )
            raise NotUniqueErrorException

    def get_acquisition_tax_calc_target_list(self):
        filters = list()
        filters.append(PublicSaleDetailModel.acquisition_tax == 0)
        query = (
            session.query(PublicSaleDetailModel)
            .with_entities(
                PublicSaleDetailModel.id,
                PublicSaleDetailModel.public_sales_id,
                PublicSaleDetailModel.private_area,
                PublicSaleDetailModel.supply_price,
                PublicSaleDetailModel.acquisition_tax,
            )
            .filter(*filters)
        )

        return query.all()

    def update_acquisition_taxes(self, update_list: List[dict]) -> None:
        try:
            session.bulk_update_mappings(
                PublicSaleDetailModel, [update_info for update_info in update_list]
            )

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"[HouseRepository][update_acquisition_taxes] error : {e}")
            raise UpdateFailErrorException

    def get_pre_calc_administrative_target_of_real_estates(self, administrative_id):
        search_filters = list()
        search_filters.append(
            and_(
                RealEstateModel.is_available == "True",
                RealEstateModel.jibun_address.contains(
                    AdministrativeDivisionModel.name
                ),
            )
        )
        query = (
            session.query(RealEstateModel)
            .join(
                AdministrativeDivisionModel,
                AdministrativeDivisionModel.id == administrative_id,
            )
            .options(joinedload(RealEstateModel.private_sales))
            .options(joinedload(RealEstateModel.public_sales))
            .options(joinedload("public_sales.public_sale_details"))
            .filter(*search_filters)
        )
        return query.all()
