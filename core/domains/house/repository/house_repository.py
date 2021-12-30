import re
from datetime import timedelta
from enum import Enum
from typing import Optional, List, Any, Tuple, Union

from geoalchemy2 import Geometry
from sqlalchemy import and_, func, or_, literal, String, exists, Integer, case
from sqlalchemy import exc
from sqlalchemy.orm import joinedload, selectinload, contains_eager, aliased, Query
from sqlalchemy.sql.functions import _FunctionGenerator

from app.extensions.database import session
from app.extensions.utils.house_helper import HouseHelper
from app.extensions.utils.image_helper import S3Helper
from app.extensions.utils.log_helper import logger_
from app.extensions.utils.math_helper import MathHelper
from app.extensions.utils.query_helper import RawQueryHelper
from app.extensions.utils.time_helper import get_server_timestamp
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
    GeneralSupplyResultModel,
    PublicSaleDetailPhotoModel,
)
from app.persistence.model.temp_summary_supply_area_api_model import (
    TempSummarySupplyAreaApiModel,
)
from app.persistence.model.temp_supply_area_api_model import TempSupplyAreaApiModel
from core.domains.banner.entity.banner_entity import ButtonLinkEntity
from core.domains.house.dto.house_dto import (
    CoordinatesRangeDto,
    GetHousePublicDetailDto,
    UpsertInterestHouseDto,
    UpdateRecentViewListDto,
)
from core.domains.house.entity.house_entity import (
    InterestHouseListEntity,
    GetRecentViewListEntity,
    GetSearchHouseListEntity,
    GetPublicSaleOfTicketUsageEntity,
    AdministrativeDivisionEntity,
    HousePublicDetailEntity,
    DetailCalendarInfoEntity,
    SimpleCalendarInfoEntity,
    PublicSaleReportEntity,
    RealEstateLegalCodeEntity,
    AdministrativeDivisionLegalCodeEntity,
    RecentlyContractedEntity,
    PublicSaleEntity,
    MapSearchEntity,
    UpdateContractStatusTargetEntity,
    PublicSaleBoundingEntity,
    PrivateSaleBoundingEntity,
    BoundingRealEstateEntity,
    NearHouseEntity,
    CheckIdsRealEstateEntity,
    AddSupplyAreaEntity,
)
from core.domains.house.enum.house_enum import (
    BoundingLevelEnum,
    BuildTypeEnum,
    HouseTypeEnum,
    DivisionLevelEnum,
    PublicSaleStatusEnum,
    RentTypeEnum,
    BoundingPrivateTypeEnum,
    BoundingPublicTypeEnum,
    PrivateSaleContractStatusEnum,
    HousingCategoryEnum,
    CalcPyoungEnum,
    BoundingIncludePrivateEnum,
    RealTradeTypeEnum,
)
from core.domains.report.entity.report_entity import (
    TicketUsageResultForHousePublicDetailEntity,
)
from core.domains.user.dto.user_dto import GetUserDto
from core.exceptions import NotUniqueErrorException, UpdateFailErrorException

logger = logger_.getLogger(__name__)


class HouseRepository:
    def create_interest_house(self, dto: UpsertInterestHouseDto) -> None:
        try:
            interest_house = InterestHouseModel(
                user_id=dto.user_id, house_id=dto.house_id, type=dto.type, is_like=True,
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
                .update({"is_like": dto.is_like})
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

    def get_bounding_private_type_filter(self, private_type: int) -> List:
        private_filter = list()
        private_filter.append(PrivateSaleModel.is_available == "True")

        if private_type == BoundingPrivateTypeEnum.APT_ONLY.value:
            private_filter.append(
                PrivateSaleModel.building_type == BuildTypeEnum.APARTMENT.value,
            )
        elif private_type == BoundingPrivateTypeEnum.OP_ONLY.value:
            private_filter.append(
                PrivateSaleModel.building_type == BuildTypeEnum.STUDIO.value,
            )
        return private_filter

    def get_bounding_public_type_filter(self, public_type: int) -> List:
        public_filter = list()
        public_filter.append(PublicSaleModel.is_available == "True")

        if public_type == BoundingPublicTypeEnum.PUBLIC_ONLY.value:
            public_filter.append(
                and_(
                    PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE.value,
                    PublicSaleModel.housing_category
                    == HousingCategoryEnum.PUBLIC.value,
                )
            )
        elif public_type == BoundingPublicTypeEnum.PRIVATE_ONLY.value:
            public_filter.append(
                and_(
                    PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE.value,
                    PublicSaleModel.housing_category
                    == HousingCategoryEnum.PRIVATE.value,
                )
            )
        elif public_type == BoundingPublicTypeEnum.ALL_PRE_SALE.value:
            public_filter.append(
                PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE.value,
            )

        return public_filter

    def get_bounding_pyoung_filter(
        self, min_area: int, max_area: int
    ) -> Optional[List]:
        pyoung_filters = list()

        if not min_area or not max_area:
            pyoung_filters.append(
                PrivateSaleAvgPriceModel.default_pyoung
                == PrivateSaleAvgPriceModel.pyoung
            )
            return pyoung_filters

        pyoung_filters.append(
            HouseHelper.convert_area_to_pyoung(PrivateSaleAvgPriceModel.pyoung)
            >= min_area
        )
        pyoung_filters.append(
            HouseHelper.convert_area_to_pyoung(PrivateSaleAvgPriceModel.pyoung)
            <= max_area
        )

        return pyoung_filters

    def get_bounding(
        self,
        bounding_filter: _FunctionGenerator,
        private_filters: List[Any],
        public_filters: List[Any],
        public_status_filters: List[int],
        include_private: Optional[int],
        min_area: Optional[int],
        max_area: Optional[int],
    ) -> Union[List[BoundingRealEstateEntity], List]:
        filters = list()
        filters.append(bounding_filter)
        filters.append(and_(RealEstateModel.is_available == "True",))

        private_results = list()
        public_results = list()

        real_estate_sub_query = (
            session.using_bind("read_only").query(RealEstateModel).filter(*filters)
        ).subquery()

        if include_private == BoundingIncludePrivateEnum.INCLUDE.value:
            trade_pyoung_filters = list()
            deposit_pyoung_filters = list()
            pyoung_case = case(
                [
                    (
                        PrivateSaleAvgPriceModel.pyoung_div == "S",
                        func.round(
                            PrivateSaleAvgPriceModel.pyoung
                            / CalcPyoungEnum.CALC_VAR.value
                        ),
                    )
                ],
                else_=func.round(
                    (
                        PrivateSaleAvgPriceModel.pyoung
                        * CalcPyoungEnum.TEMP_CALC_VAR.value
                    )
                    / CalcPyoungEnum.CALC_VAR.value
                ),
            )

            if (min_area or min_area == 0) and max_area:
                trade_pyoung_filters.append(pyoung_case >= min_area)
                trade_pyoung_filters.append(pyoung_case <= max_area)
                deposit_pyoung_filters.append(pyoung_case >= min_area)
                deposit_pyoung_filters.append(pyoung_case <= max_area)

            """
                # (1) 면적 필터가 없을 때는 default_pyoung 기준으로 보여줌
                      * 아파트 또는 오피스텔에 매매정보가 없어도 보여줌 (left outer join)
                
                # (2) 면적 필터가 있을 때는 면적 필터 범위안에서 계약일이 가장 최근의 것 하나를 보여줌
                      * 아파트 또는 오피스텔에 매매정보가 없으면 안보여줌 (inner join)
                        * 평수 필터에서 해당 평수가 존재하지 않으면 맵에서 안보여주기로 했기 때문에
            """
            if not trade_pyoung_filters:
                # (1)
                private_trade_query = (
                    session.using_bind("read_only")
                    .query(real_estate_sub_query)
                    .with_entities(
                        real_estate_sub_query.c.id.label("real_estate_id"),
                        real_estate_sub_query.c.jibun_address.label("jibun_address"),
                        real_estate_sub_query.c.road_address.label("road_address"),
                        real_estate_sub_query.c.coordinates.ST_Y().label("latitude"),
                        real_estate_sub_query.c.coordinates.ST_X().label("longitude"),
                        PrivateSaleModel.id.label("id"),
                        PrivateSaleModel.building_type.label("building_type"),
                        PrivateSaleModel.name.label("name"),
                        pyoung_case.label("trade_pyoung"),
                        PrivateSaleAvgPriceModel.trade_price.label("trade_price"),
                        literal(None, None).label("deposit_pyoung"),
                        literal(None, None).label("deposit_price"),
                        func.coalesce(PrivateSaleModel.trade_status, 0).label(
                            "trade_status"
                        ),
                        literal(0, None).label("deposit_status"),
                    )
                    .join(
                        PrivateSaleModel,
                        PrivateSaleModel.real_estate_id == real_estate_sub_query.c.id,
                    )
                    .join(
                        PrivateSaleAvgPriceModel,
                        (
                            PrivateSaleAvgPriceModel.private_sales_id
                            == PrivateSaleModel.id
                        )
                        & (
                            PrivateSaleAvgPriceModel.default_trade_pyoung
                            == PrivateSaleAvgPriceModel.pyoung
                        ),
                        isouter=True,
                    )
                    .filter(*private_filters)
                )

                private_deposit_query = (
                    session.using_bind("read_only")
                    .query(real_estate_sub_query)
                    .with_entities(
                        real_estate_sub_query.c.id.label("real_estate_id"),
                        real_estate_sub_query.c.jibun_address.label("jibun_address"),
                        real_estate_sub_query.c.road_address.label("road_address"),
                        real_estate_sub_query.c.coordinates.ST_Y().label("latitude"),
                        real_estate_sub_query.c.coordinates.ST_X().label("longitude"),
                        PrivateSaleModel.id.label("id"),
                        PrivateSaleModel.building_type.label("building_type"),
                        PrivateSaleModel.name.label("name"),
                        literal(None, None).label("trade_pyoung"),
                        literal(None, None).label("trade_price"),
                        pyoung_case.label("deposit_pyoung"),
                        PrivateSaleAvgPriceModel.deposit_price.label("deposit_price"),
                        literal(0, None).label("trade_status"),
                        func.coalesce(PrivateSaleModel.deposit_status, 0).label(
                            "deposit_status"
                        ),
                    )
                    .join(
                        PrivateSaleModel,
                        PrivateSaleModel.real_estate_id == real_estate_sub_query.c.id,
                    )
                    .join(
                        PrivateSaleAvgPriceModel,
                        (
                            PrivateSaleAvgPriceModel.private_sales_id
                            == PrivateSaleModel.id
                        )
                        & (
                            PrivateSaleAvgPriceModel.default_deposit_pyoung
                            == PrivateSaleAvgPriceModel.pyoung
                        ),
                        isouter=True,
                    )
                    .filter(*private_filters)
                )

                union_q = private_trade_query.union_all(
                    private_deposit_query
                ).subquery()
                private_query = (
                    session.using_bind("read_only")
                    .query(union_q)
                    .with_entities(
                        func.max(union_q.c.real_estate_id).label("real_estate_id"),
                        func.max(union_q.c.jibun_address).label("jibun_address"),
                        func.max(union_q.c.road_address).label("road_address"),
                        func.max(union_q.c.latitude).label("latitude"),
                        func.max(union_q.c.longitude).label("longitude"),
                        union_q.c.id,
                        func.max(union_q.c.building_type).label("building_type"),
                        func.max(union_q.c.name).label("name"),
                        func.max(union_q.c.trade_pyoung).label("trade_pyoung"),
                        func.max(union_q.c.trade_price).label("trade_price"),
                        func.max(union_q.c.deposit_pyoung).label("deposit_pyoung"),
                        func.max(union_q.c.deposit_price).label("deposit_price"),
                        func.max(union_q.c.trade_status).label("trade_status"),
                        func.max(union_q.c.deposit_status).label("deposit_status"),
                    )
                    .group_by(union_q.c.id)
                )
                query_set = private_query.all()
            else:
                # (2)
                # private_sales 매매 조회
                # 가장 최근 계약일 기준으로 매매가 조회
                private_trade_sub_q = (
                    session.using_bind("read_only")
                    .query(real_estate_sub_query)
                    .with_entities(
                        real_estate_sub_query.c.id.label("real_estate_id"),
                        real_estate_sub_query.c.jibun_address,
                        real_estate_sub_query.c.road_address,
                        real_estate_sub_query.c.coordinates.ST_Y().label("latitude"),
                        real_estate_sub_query.c.coordinates.ST_X().label("longitude"),
                        PrivateSaleModel.id,
                        PrivateSaleModel.building_type,
                        PrivateSaleModel.name,
                        func.coalesce(PrivateSaleModel.trade_status, 0).label(
                            "trade_status"
                        ),
                        literal(0, None).label("deposit_status"),
                        pyoung_case.label("pyoung"),
                        PrivateSaleAvgPriceModel.trade_price,
                        PrivateSaleAvgPriceModel.max_trade_contract_date,
                        func.row_number()
                        .over(
                            partition_by=PrivateSaleModel.id,
                            order_by=func.coalesce(
                                PrivateSaleAvgPriceModel.max_trade_contract_date,
                                "19000101",
                            ).desc(),
                        )
                        .label("trade_rank"),
                    )
                    .join(
                        PrivateSaleModel,
                        PrivateSaleModel.real_estate_id == real_estate_sub_query.c.id,
                    )
                    .join(
                        PrivateSaleAvgPriceModel,
                        PrivateSaleAvgPriceModel.private_sales_id
                        == PrivateSaleModel.id,
                    )
                    .filter(*private_filters)
                    .filter(*trade_pyoung_filters)
                    .filter(PrivateSaleAvgPriceModel.trade_price > 0)
                ).subquery()

                private_trade_query = (
                    session.using_bind("read_only")
                    .query(private_trade_sub_q)
                    .with_entities(
                        func.max(private_trade_sub_q.c.real_estate_id).label(
                            "real_estate_id"
                        ),
                        func.max(private_trade_sub_q.c.jibun_address).label(
                            "jibun_address"
                        ),
                        func.max(private_trade_sub_q.c.road_address).label(
                            "road_address"
                        ),
                        func.max(private_trade_sub_q.c.latitude).label("latitude"),
                        func.max(private_trade_sub_q.c.longitude).label("longitude"),
                        private_trade_sub_q.c.id.label("id"),
                        func.max(private_trade_sub_q.c.building_type).label(
                            "building_type"
                        ),
                        func.max(private_trade_sub_q.c.name).label("name"),
                        func.max(private_trade_sub_q.c.trade_status).label(
                            "trade_status"
                        ),
                        func.max(private_trade_sub_q.c.deposit_status).label(
                            "deposit_status"
                        ),
                        func.max(private_trade_sub_q.c.pyoung).label("trade_pyoung"),
                        func.max(private_trade_sub_q.c.trade_price).label(
                            "trade_price"
                        ),
                        literal(None, None).label("deposit_pyoung"),
                        literal(None, None).label("deposit_price"),
                    )
                    .group_by(
                        private_trade_sub_q.c.id, private_trade_sub_q.c.trade_rank,
                    )
                    .having(private_trade_sub_q.c.trade_rank == 1)
                )

                # private_sales 전세 조회
                # 가장 최근 계약일 기준으로 전세가 조회
                private_deposit_sub_q = (
                    session.using_bind("read_only")
                    .query(real_estate_sub_query)
                    .with_entities(
                        real_estate_sub_query.c.id.label("real_estate_id"),
                        real_estate_sub_query.c.jibun_address,
                        real_estate_sub_query.c.road_address,
                        real_estate_sub_query.c.coordinates.ST_Y().label("latitude"),
                        real_estate_sub_query.c.coordinates.ST_X().label("longitude"),
                        PrivateSaleModel.id,
                        PrivateSaleModel.building_type,
                        PrivateSaleModel.name,
                        literal(0, None).label("trade_status"),
                        func.coalesce(PrivateSaleModel.deposit_status, 0).label(
                            "deposit_status"
                        ),
                        pyoung_case.label("pyoung"),
                        PrivateSaleAvgPriceModel.deposit_price,
                        PrivateSaleAvgPriceModel.max_deposit_contract_date,
                        func.row_number()
                        .over(
                            partition_by=PrivateSaleModel.id,
                            order_by=func.coalesce(
                                PrivateSaleAvgPriceModel.max_deposit_contract_date,
                                "19000101",
                            ).desc(),
                        )
                        .label("deposit_rank"),
                    )
                    .join(
                        PrivateSaleModel,
                        PrivateSaleModel.real_estate_id == real_estate_sub_query.c.id,
                    )
                    .join(
                        PrivateSaleAvgPriceModel,
                        PrivateSaleAvgPriceModel.private_sales_id
                        == PrivateSaleModel.id,
                    )
                    .filter(*private_filters)
                    .filter(*deposit_pyoung_filters)
                    .filter(PrivateSaleAvgPriceModel.deposit_price > 0)
                ).subquery()

                private_deposit_query = (
                    session.using_bind("read_only")
                    .query(private_deposit_sub_q)
                    .with_entities(
                        func.max(private_deposit_sub_q.c.real_estate_id).label(
                            "real_estate_id"
                        ),
                        func.max(private_deposit_sub_q.c.jibun_address).label(
                            "jibun_address"
                        ),
                        func.max(private_deposit_sub_q.c.road_address).label(
                            "road_address"
                        ),
                        func.max(private_deposit_sub_q.c.latitude).label("latitude"),
                        func.max(private_deposit_sub_q.c.longitude).label("longitude"),
                        private_deposit_sub_q.c.id.label("id"),
                        func.max(private_deposit_sub_q.c.building_type).label(
                            "building_type"
                        ),
                        func.max(private_deposit_sub_q.c.name).label("name"),
                        func.max(private_deposit_sub_q.c.trade_status).label(
                            "trade_status"
                        ),
                        func.max(private_deposit_sub_q.c.deposit_status).label(
                            "deposit_status"
                        ),
                        literal(None, None).label("trade_pyoung"),
                        literal(None, None).label("trade_price"),
                        func.max(private_deposit_sub_q.c.pyoung).label(
                            "deposit_pyoung"
                        ),
                        func.max(private_deposit_sub_q.c.deposit_price).label(
                            "deposit_price"
                        ),
                    )
                    .group_by(
                        private_deposit_sub_q.c.id,
                        private_deposit_sub_q.c.deposit_rank,
                    )
                    .having(private_deposit_sub_q.c.deposit_rank == 1)
                )

                union_q = private_trade_query.union_all(
                    private_deposit_query
                ).subquery()
                final_query = (
                    session.using_bind("read_only")
                    .query(union_q)
                    .with_entities(
                        func.max(union_q.c.real_estate_id).label("real_estate_id"),
                        func.max(union_q.c.jibun_address).label("jibun_address"),
                        func.max(union_q.c.road_address).label("road_address"),
                        func.max(union_q.c.latitude).label("latitude"),
                        func.max(union_q.c.longitude).label("longitude"),
                        union_q.c.id.label("id"),
                        func.max(union_q.c.building_type).label("building_type"),
                        func.max(union_q.c.name).label("name"),
                        func.max(union_q.c.trade_status).label("trade_status"),
                        func.max(union_q.c.deposit_status).label("deposit_status"),
                        func.max(union_q.c.trade_pyoung).label("trade_pyoung"),
                        func.max(union_q.c.trade_price).label("trade_price"),
                        func.max(union_q.c.deposit_pyoung).label("deposit_pyoung"),
                        func.max(union_q.c.deposit_price).label("deposit_price"),
                    )
                    .group_by(union_q.c.id,)
                )
                query_set = final_query.all()

            if query_set:
                for query in query_set:
                    private_results.append(
                        PrivateSaleBoundingEntity(
                            real_estate_id=query.real_estate_id,
                            jibun_address=query.jibun_address,
                            road_address=query.road_address,
                            latitude=query.latitude,
                            longitude=query.longitude,
                            private_sales_id=query.id,
                            building_type=query.building_type,
                            name=query.name,
                            trade_status=query.trade_status,
                            deposit_status=query.deposit_status,
                            trade_pyoung=None
                            if query.trade_pyoung == 0
                            else query.trade_pyoung,
                            trade_price=None
                            if query.trade_price == 0
                            else query.trade_price,
                            deposit_pyoung=None
                            if query.deposit_pyoung == 0
                            else query.deposit_pyoung,
                            deposit_price=None
                            if query.deposit_price == 0
                            else query.deposit_price,
                        )
                    )

        # -------------------- 매매 쿼리 종료 --------------------

        # 분양 건 조회
        public_query = (
            session.using_bind("read_only")
            .query(real_estate_sub_query)
            .with_entities(
                real_estate_sub_query.c.id.label("real_estate_id"),
                real_estate_sub_query.c.jibun_address,
                real_estate_sub_query.c.road_address,
                real_estate_sub_query.c.coordinates.ST_Y().label("latitude"),
                real_estate_sub_query.c.coordinates.ST_X().label("longitude"),
                PublicSaleModel.id,
                PublicSaleModel.housing_category,
                PublicSaleModel.name,
                PublicSaleModel.offer_date,
                PublicSaleModel.subscription_end_date,
                PublicSaleAvgPriceModel.pyoung,
                PublicSaleAvgPriceModel.supply_price,
                PublicSaleAvgPriceModel.avg_competition,
                PublicSaleAvgPriceModel.min_score,
            )
            .join(
                PublicSaleModel,
                PublicSaleModel.real_estate_id == real_estate_sub_query.c.id,
            )
            .join(
                PublicSaleAvgPriceModel,
                PublicSaleAvgPriceModel.public_sales_id == PublicSaleModel.id,
            )
            .filter(*public_filters)
        )
        query_set = public_query.all()

        if query_set:
            for query in query_set:
                status = HouseHelper.public_status(
                    offer_date=query.offer_date,
                    subscription_end_date=query.subscription_end_date,
                )

                avg_competition, min_score = None, None
                if status >= PublicSaleStatusEnum.IS_CLOSED.value:
                    avg_competition = HouseHelper.convert_avg_competition(
                        avg_competition=query.avg_competition
                    )
                    min_score = HouseHelper.convert_min_score(min_score=query.min_score)

                public_results.append(
                    PublicSaleBoundingEntity(
                        real_estate_id=query.real_estate_id,
                        jibun_address=query.jibun_address,
                        road_address=query.road_address,
                        latitude=query.latitude,
                        longitude=query.longitude,
                        public_sales_id=query.id,
                        housing_category=query.housing_category,
                        name=query.name,
                        status=status,
                        pyoung=query.pyoung,
                        supply_price=query.supply_price,
                        avg_competition=avg_competition,
                        min_score=min_score,
                    )
                )

        result = list()
        for private_sales in private_results:
            result.append(BoundingRealEstateEntity(private_sales=private_sales))

        for public_sales in public_results:
            if public_sales.status in public_status_filters:
                result.append(BoundingRealEstateEntity(public_sales=public_sales))

        return result

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
        filters.append(AdministrativeDivisionModel.is_available == "True")
        query = (
            session.using_bind("read_only")
            .query(AdministrativeDivisionModel)
            .filter(*filters)
        )
        queryset = query.all()

        return self._make_bounding_administrative_entity(queryset=queryset)

    def _is_enable_real_estate(self, real_estate_id: int) -> bool:
        real_estate = (
            session.using_bind("read_only")
            .query(RealEstateModel)
            .filter_by(id=real_estate_id)
            .first()
        )

        if not real_estate or real_estate.is_available == "False":
            return False
        return True

    def is_enable_public_sale_house(self, house_id: int) -> bool:
        try:
            house = (
                session.using_bind("read_only")
                .query(PublicSaleModel)
                .filter_by(id=house_id)
                .first()
            )
        except Exception:
            house = None

        if not house or house.is_available == "False":
            return False
        elif not self._is_enable_real_estate(house.real_estate_id):
            return False
        return True

    def is_enable_public_sale_detail_info(self, public_sale_details_id: int) -> bool:
        try:
            detail_info = (
                session.using_bind("read_only")
                .query(PublicSaleDetailModel)
                .filter_by(id=public_sale_details_id)
                .first()
            )
        except Exception:
            detail_info = None

        if not detail_info or detail_info.public_sales.is_available == "False":
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

        interest_house = (
            session.using_bind("read_only")
            .query(InterestHouseModel)
            .filter(*filters)
            .first()
        )

        if not interest_house:
            return None
        return interest_house

    def get_house_with_public_sales(self, house_id: int) -> Tuple[Any, Any]:
        filters = list()
        filters.append(
            and_(
                RealEstateModel.is_available == "True",
                PublicSaleModel.is_available == "True",
                PublicSaleModel.id == house_id,
                PublicSaleModel.real_estate_id == RealEstateModel.id,
                PublicSaleDetailModel.public_sales_id == PublicSaleModel.id,
            )
        )
        query = (
            session.using_bind("read_only")
            .query(
                PublicSaleModel,
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
                func.min(PublicSaleDetailModel.supply_price).label("min_supply_price"),
                func.max(PublicSaleDetailModel.supply_price).label("max_supply_price"),
            )
            .options(joinedload(PublicSaleModel.real_estates, innerjoin=True))
            .options(joinedload(PublicSaleModel.public_sale_details, innerjoin=True))
            .options(joinedload(PublicSaleModel.public_sale_photos))
            .options(joinedload("public_sale_details.public_sale_detail_photos"))
            .options(joinedload("public_sale_details.special_supply_results"))
            .options(joinedload("public_sale_details.general_supply_results"))
            .filter(*filters)
            .group_by(PublicSaleModel.id)
        )
        query_set = query.first()

        return query_set, query_set[0].housing_category

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
        ticket_usage_results: Optional[TicketUsageResultForHousePublicDetailEntity],
    ) -> HousePublicDetailEntity:
        # (<PublicSaleModel>, [0]
        # min_supply_area, [1]
        # max_supply_area, [2]
        # avg_supply_price, [3]
        # avg_supply_area,  [4]
        # min_acquisition_tax [5]
        # max_acquisition_tax, [6]
        # min_supply_price, [7]
        # max_supply_price) [8]
        return house_with_public_sales[0].to_house_with_public_detail_entity(
            is_like=is_like,
            min_pyoung_number=HouseHelper.convert_area_to_pyoung(
                house_with_public_sales[1]
            ),
            max_pyoung_number=HouseHelper.convert_area_to_pyoung(
                house_with_public_sales[2]
            ),
            min_supply_area=house_with_public_sales[1],
            max_supply_area=house_with_public_sales[2],
            avg_supply_price=house_with_public_sales[3],
            supply_price_per_pyoung=self._get_supply_price_per_pyoung(
                supply_price=float(house_with_public_sales[3]),
                avg_pyoung_number=HouseHelper.convert_area_to_pyoung(
                    house_with_public_sales[4]
                ),
            ),
            min_acquisition_tax=house_with_public_sales[5],
            max_acquisition_tax=house_with_public_sales[6],
            button_links=button_link_list,
            ticket_usage_results=ticket_usage_results,
            min_supply_price=house_with_public_sales[7],
            max_supply_price=house_with_public_sales[8],
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
                PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE.value,
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
            session.using_bind("read_only")
            .query(RealEstateModel)
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
            session.using_bind("read_only")
            .query(InterestHouseModel)
            .with_entities(
                InterestHouseModel.house_id,
                InterestHouseModel.type,
                InterestHouseModel.updated_at,
                PublicSaleModel.name.label("name"),
                RealEstateModel.jibun_address,
                RealEstateModel.road_address,
                PublicSaleModel.subscription_start_date.label(
                    "subscription_start_date"
                ),
                PublicSaleModel.subscription_end_date.label("subscription_end_date"),
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
            .join(
                PublicSalePhotoModel,
                (PublicSalePhotoModel.public_sales_id == PublicSaleModel.id)
                & (PublicSalePhotoModel.is_thumbnail == "True"),
                isouter=True,
            )
        )

        private_sales_query = (
            session.using_bind("read_only")
            .query(InterestHouseModel)
            .with_entities(
                InterestHouseModel.house_id,
                InterestHouseModel.type,
                InterestHouseModel.updated_at,
                PrivateSaleModel.name.label("name"),
                RealEstateModel.jibun_address,
                RealEstateModel.road_address,
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

        union_query = public_sales_query.union_all(private_sales_query).subquery()

        query = (
            session.using_bind("read_only")
            .query(union_query)
            .order_by(union_query.c.interest_houses_updated_at.desc())
        )
        query_set = query.all()

        return self._make_interest_house_list_entity(queryset=query_set)

    def _make_interest_house_list_entity(
        self, queryset: Optional[List]
    ) -> List[InterestHouseListEntity]:

        result = list()

        if queryset:
            for query in queryset:
                result.append(
                    InterestHouseListEntity(
                        house_id=query.interest_houses_house_id,
                        type=query.interest_houses_type,
                        name=query.name,
                        jibun_address=query.real_estates_jibun_address,
                        road_address=query.real_estates_road_address,
                        subscription_start_date=query.subscription_start_date,
                        subscription_end_date=query.subscription_end_date,
                        image_path=S3Helper.get_cloudfront_url()
                        + "/"
                        + query.image_path
                        if query.image_path
                        else None,
                    )
                )

        return result

    def get_interest_house(
        self, user_id: int, house_id: int
    ) -> Optional[InterestHouseListEntity]:
        query = (
            session.using_bind("read_only")
            .query(InterestHouseModel)
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
            .join(
                PublicSalePhotoModel,
                (PublicSalePhotoModel.public_sales_id == InterestHouseModel.house_id)
                & (PublicSalePhotoModel.is_thumbnail == True),
                isouter=True,
            )
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
            image_path=S3Helper().get_cloudfront_url() + "/" + queryset.image_path
            if queryset.image_path
            else None,
        )

    def get_recent_view_list(self, dto: GetUserDto) -> List[GetRecentViewListEntity]:
        # private_sales 는 X -> MVP 에서는 매매 상세화면이 없음
        query = (
            session.using_bind("read_only")
            .query(RecentlyViewModel)
            .with_entities(
                func.max(RecentlyViewModel.id).label("id"),
                RecentlyViewModel.house_id,
                RecentlyViewModel.type,
                func.max(RecentlyViewModel.updated_at).label("updated_at"),
                func.max(PublicSaleModel.name).label("name"),
                func.max(PublicSalePhotoModel.path).label("path"),
            )
            .join(
                PublicSaleModel,
                (RecentlyViewModel.house_id == PublicSaleModel.id)
                & (RecentlyViewModel.type == HouseTypeEnum.PUBLIC_SALES.value)
                & (RecentlyViewModel.user_id == dto.user_id)
                & (RecentlyViewModel.is_available == True),
            )
            .join(
                PublicSalePhotoModel,
                (PublicSalePhotoModel.public_sales_id == PublicSaleModel.id)
                & (PublicSalePhotoModel.is_thumbnail == True),
                isouter=True,
            )
            .group_by(RecentlyViewModel.house_id, RecentlyViewModel.type,)
        )

        sub_query = query.subquery()
        sub_q = aliased(sub_query)

        query = (
            session.using_bind("read_only")
            .query(sub_q)
            .order_by(sub_q.c.updated_at.desc())
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
                        id=query.id,
                        house_id=query.house_id,
                        type=query.type,
                        name=query.name,
                        image_path=S3Helper.get_cloudfront_url() + "/" + query.path
                        if query.path
                        else None,
                    )
                )

        return result

    def update_recent_view_list(self, dto: UpdateRecentViewListDto) -> None:
        filters = list()
        filters.append(RecentlyViewModel.id == dto.id)

        try:
            session.query(RecentlyViewModel).filter(*filters).update(
                {"is_available": False}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][update_recent_view_list] user_id : {dto.user_id} error : {e}"
            )
            raise Exception(e)

    def _make_get_search_house_list_entity(
        self, queryset: Optional[List], user_id: int
    ) -> List[GetSearchHouseListEntity]:
        search_entities = list()

        if queryset:
            for query in queryset:
                # (더 이상 사용안함) 찜한 여부 제거 (퍼포먼스 이슈) -> 무조건 false 반환
                # is_like = self.is_user_liked_house(
                #     self.get_public_interest_house(
                #         dto=GetHousePublicDetailDto(user_id=user_id, house_id=query.id)
                #     )
                # )
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
                        is_like=False,
                        image_path=S3Helper.get_cloudfront_url() + "/" + query.path
                        if query.path
                        else None,
                        subscription_start_date=query.subscription_start_date,
                        subscription_end_date=query.subscription_end_date,
                        status=HouseHelper().public_status(
                            offer_date=query.offer_date,
                            subscription_end_date=query.subscription_end_date,
                        ),
                        avg_down_payment=avg_down_payment,
                        avg_supply_price=query.avg_supply_price
                        if query.avg_supply_price
                        else 0,
                    )
                )

        return search_entities

    def get_search_house_list(self, keywords: str) -> List[MapSearchEntity]:
        """
            todo: 검색 성능 고도화 필요, private_sales 붙이므로 front 화면 변경 필요 (핑퐁 작업 필요)
            - full_scan 방식
            - %LIKE% : 서로 다른 두 단어부터 검색 불가
            - Full Text Search 필요(ts_vector, pg_trgm, elastic_search...)
        """
        public_filters = list()
        private_filters = list()

        public_text_keyword_filters = list()
        private_text_keyword_filters = list()

        public_number_keyword_filters = list()
        private_number_keyword_filters = list()

        public_filters.append(
            and_(
                RealEstateModel.is_available == "True",
                PublicSaleModel.is_available == "True",
                PublicSaleModel.rent_type != RentTypeEnum.RENTAL.value,
            ),
        )

        private_filters.append(
            and_(
                RealEstateModel.is_available == "True",
                PrivateSaleModel.building_type != BuildTypeEnum.ROW_HOUSE.value,
            ),
        )

        hangul = re.compile("[^ ㄱ-ㅣ가-힣]+")
        split_numbers = hangul.findall(keywords)

        split_list = list()
        for split_number in split_numbers:
            split_list.append(keywords.split(split_number))

        # 리스트안의 리스트 합치기
        split_list = sum(split_list, [])

        # 공백 원소 제거
        split_list = list(filter(bool, split_list))
        split_keywords = list()
        for split_text in split_list:
            # 띄어쓰기 분리
            text = split_text.split()
            for c in text:
                split_keywords.append(c)

        # 검색 효율 떨어뜨리는 문자 제거
        # word_list = ["단지", "아파트", "마을", "0"]
        # for word in word_list:
        #     if word in split_list:
        #         split_list.remove(word)

        split_set = set(split_keywords)

        # text 검색 키워드
        for split_text in split_set:
            public_text_keyword_filters.append(
                (PublicSaleModel.name.contains(split_text))
            )
            private_text_keyword_filters.append(
                (PrivateSaleModel.name.contains(split_text))
            )

        # 숫자 검색 키워드
        for split_number in split_numbers:
            public_number_keyword_filters.append(
                (PublicSaleModel.name.contains(split_number))
            )
            private_number_keyword_filters.append(
                (PrivateSaleModel.name.contains(split_number))
            )

        if not split_set:
            # 띄어쓰기로 Like 검색
            split_keywords = keywords.split()

            # 검색 효율 떨어뜨리는 문자 제거
            # for word in word_list:
            #     if word in split_keywords:
            #         split_keywords.remove(word)

            for split_keyword in split_keywords:
                public_text_keyword_filters.append(
                    PublicSaleModel.name.contains(split_keyword),
                )
                private_text_keyword_filters.append(
                    PrivateSaleModel.name.contains(split_keyword),
                )

        query_cond1 = (
            session.using_bind("read_only")
            .query(PublicSaleModel)
            .with_entities(
                RealEstateModel.id,
                PublicSaleModel.name.label("name"),
                RealEstateModel.coordinates.ST_Y().label("latitude"),
                RealEstateModel.coordinates.ST_X().label("longitude"),
                literal("분양", String).label("house_type"),
            )
            .join(RealEstateModel, RealEstateModel.id == PublicSaleModel.real_estate_id)
            .filter(*public_filters)
            .filter(and_(*public_text_keyword_filters, *public_number_keyword_filters),)
            .order_by((RealEstateModel.si_do == "서울특별시").desc())
            .order_by((RealEstateModel.si_do == "경기도").desc())
            .order_by(RealEstateModel.id.asc())
            .limit(10)
        )

        query_cond2 = (
            session.using_bind("read_only")
            .query(PrivateSaleModel)
            .with_entities(
                RealEstateModel.id,
                (RealEstateModel.dong_myun + " " + PrivateSaleModel.name).label("name"),
                RealEstateModel.coordinates.ST_Y().label("latitude"),
                RealEstateModel.coordinates.ST_X().label("longitude"),
                literal("매매", String).label("house_type"),
            )
            .join(
                RealEstateModel, RealEstateModel.id == PrivateSaleModel.real_estate_id
            )
            .filter(*private_filters)
            .filter(
                and_(*private_text_keyword_filters, *private_number_keyword_filters),
            )
            .order_by((RealEstateModel.si_do == "서울특별시").desc())
            .order_by((RealEstateModel.si_do == "경기도").desc())
            .order_by(RealEstateModel.id.asc())
            .limit(15)
        )

        query = query_cond1.union_all(query_cond2)
        query_set = query.all()

        result = list()
        for query in query_set:
            result.append(
                MapSearchEntity(
                    id=query[0],
                    name=query[1],
                    latitude=query[2],
                    longitude=query[3],
                    house_type=query[4],
                )
            )

        return result

    def get_geometry_coordinates_from_real_estate(
        self, real_estate_id: int
    ) -> Optional[Geometry]:
        real_estate = (
            session.using_bind("read_only")
            .query(RealEstateModel)
            .filter_by(id=real_estate_id)
            .first()
        )

        if real_estate:
            return real_estate.coordinates
        return None

    def get_geometry_coordinates_from_public_sale(
        self, public_sale_id: int
    ) -> Optional[Geometry]:
        public_sale = (
            session.using_bind("read_only")
            .query(PublicSaleModel)
            .filter_by(id=public_sale_id)
            .first()
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
            session.using_bind("read_only")
            .query(AdministrativeDivisionModel)
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
            session.using_bind("read_only")
            .query(PublicSaleModel)
            .join(
                PublicSalePhotoModel,
                (PublicSalePhotoModel.public_sales_id == PublicSaleModel.id)
                & (PublicSalePhotoModel.is_thumbnail == True),
                isouter=True,
            )
            .options(contains_eager(PublicSaleModel.public_sale_photos))
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
                        image_path=S3Helper.get_cloudfront_url()
                        + "/"
                        + query.public_sale_photos[0].path
                        if query.public_sale_photos
                        else None,
                    )
                )
        return result

    def get_public_sale_info(self, house_id: int) -> PublicSaleReportEntity:
        query = (
            session.using_bind("read_only")
            .query(PublicSaleModel)
            .options(joinedload(PublicSaleModel.real_estates, innerjoin=True))
            .options(joinedload(PublicSaleModel.public_sale_details, innerjoin=True))
            .options(joinedload(PublicSaleModel.public_sale_photos))
            .options(joinedload("public_sale_details.public_sale_detail_photos"))
            .options(joinedload("public_sale_details.special_supply_results"))
            .options(joinedload("public_sale_details.general_supply_results"))
            .filter(PublicSaleModel.id == house_id)
        )
        query_set = query.first()

        return query_set.to_report_entity()

    def get_recently_public_sale_info(
        self, report_public_sale_infos: PublicSaleReportEntity
    ) -> PublicSaleReportEntity:
        filters = list()
        filters.append(
            and_(
                RealEstateModel.si_do == report_public_sale_infos.real_estates.si_do,
                RealEstateModel.si_gun_gu
                == report_public_sale_infos.real_estates.si_gun_gu,
            )
        )
        filters.append(PublicSaleModel.is_available == True)
        filters.append(PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE.value)
        filters.append(
            PublicSaleModel.subscription_end_date
            < get_server_timestamp().strftime("%Y%m%d")
        )
        query = (
            session.using_bind("read_only")
            .query(PublicSaleModel)
            .join(
                RealEstateModel,
                (RealEstateModel.id == PublicSaleModel.real_estate_id)
                & (
                    RealEstateModel.si_gun_gu
                    == report_public_sale_infos.real_estates.si_gun_gu
                ),
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
        if not query_set:
            longitude = report_public_sale_infos.real_estates.longitude
            latitude = report_public_sale_infos.real_estates.latitude
            point = f"SRID=4326;POINT({longitude} {latitude})"

            filters = list()
            filters.append(PublicSaleModel.is_available == True)
            filters.append(PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE.value)
            filters.append(
                PublicSaleModel.subscription_end_date
                < get_server_timestamp().strftime("%Y%m%d")
            )

            sub_query = (
                session.using_bind("read_only")
                .query(RealEstateModel)
                .join(
                    PublicSaleModel,
                    RealEstateModel.id == PublicSaleModel.real_estate_id,
                )
                .filter(*filters)
                .order_by(func.ST_Distance(RealEstateModel.coordinates, point))
                .limit(1)
            ).subquery()

            query = (
                session.using_bind("read_only")
                .query(PublicSaleModel)
                .join(sub_query, (sub_query.c.id == PublicSaleModel.real_estate_id))
                .options(
                    joinedload(PublicSaleModel.public_sale_details, innerjoin=True)
                )
                .options(joinedload("public_sale_details.public_sale_detail_photos"))
                .options(joinedload("public_sale_details.special_supply_results"))
                .options(joinedload("public_sale_details.general_supply_results"))
                .options(joinedload(PublicSaleModel.public_sale_photos))
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

        sub_query_cond_1 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                func.to_char(
                    func.to_date(
                        func.max(PrivateSaleDetailModel.contract_date), "YYYYMMDD"
                    ),
                    "YYYYMMDD",
                ).label("max_contract_date"),
                func.to_char(
                    (
                        func.to_date(
                            func.max(PrivateSaleDetailModel.contract_date), "YYYYMMDD"
                        )
                        - timedelta(days=93)
                    ),
                    "YYYYMMDD",
                ).label("min_contract_date"),
            )
            .filter(*filters)
            .filter(PrivateSaleDetailModel.trade_type == "매매")
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                PrivateSaleDetailModel.trade_type,
            )
        ).subquery()

        sub_query_cond_2 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                func.to_char(
                    func.to_date(
                        func.max(PrivateSaleDetailModel.contract_date), "YYYYMMDD"
                    ),
                    "YYYYMMDD",
                ).label("max_contract_date"),
                func.to_char(
                    (
                        func.to_date(
                            func.max(PrivateSaleDetailModel.contract_date), "YYYYMMDD"
                        )
                        - timedelta(days=93)
                    ),
                    "YYYYMMDD",
                ).label("min_contract_date"),
            )
            .filter(*filters)
            .filter(PrivateSaleDetailModel.trade_type == "전세")
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                PrivateSaleDetailModel.trade_type,
            )
        ).subquery()

        query_cond1 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                func.avg(PrivateSaleDetailModel.trade_price).label("avg_trade_price"),
                literal(0, Integer).label("avg_deposit_price"),
                sub_query_cond_1.c.max_contract_date.label("max_trade_contract_date"),
                literal(None, String).label("max_deposit_contract_date"),
            )
            .join(
                sub_query_cond_1,
                and_(
                    PrivateSaleDetailModel.private_sales_id
                    == sub_query_cond_1.c.private_sales_id,
                    PrivateSaleDetailModel.private_area
                    == sub_query_cond_1.c.private_area,
                ),
                isouter=True,
            )
            .filter(*filters)
            .filter(PrivateSaleDetailModel.trade_type == "매매")
            .filter(
                PrivateSaleDetailModel.contract_date
                >= sub_query_cond_1.c.min_contract_date
            )
            .filter(
                PrivateSaleDetailModel.contract_date
                <= sub_query_cond_1.c.max_contract_date
            )
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                sub_query_cond_1.c.min_contract_date,
                sub_query_cond_1.c.max_contract_date,
            )
        )

        query_cond2 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                literal(0, Integer).label("avg_trade_price"),
                func.avg(PrivateSaleDetailModel.deposit_price).label(
                    "avg_deposit_price"
                ),
                literal(None, String).label("max_trade_contract_date"),
                sub_query_cond_2.c.max_contract_date.label("max_deposit_contract_date"),
            )
            .join(
                sub_query_cond_2,
                and_(
                    PrivateSaleDetailModel.private_sales_id
                    == sub_query_cond_2.c.private_sales_id,
                    PrivateSaleDetailModel.private_area
                    == sub_query_cond_2.c.private_area,
                ),
                isouter=True,
            )
            .filter(*filters)
            .filter(PrivateSaleDetailModel.trade_type == "전세")
            .filter(
                PrivateSaleDetailModel.contract_date
                >= sub_query_cond_2.c.min_contract_date
            )
            .filter(
                PrivateSaleDetailModel.contract_date
                <= sub_query_cond_2.c.max_contract_date
            )
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                sub_query_cond_2.c.min_contract_date,
                sub_query_cond_2.c.max_contract_date,
            )
        )

        union_query = query_cond1.union_all(query_cond2).subquery()
        pyoung_case = case(
            [
                (
                    and_(
                        union_query.columns.private_sale_details_supply_area != 0,
                        union_query.columns.private_sale_details_supply_area != None,
                    ),
                    union_query.columns.private_sale_details_supply_area,
                ),
                (
                    union_query.columns.private_sale_details_supply_area == 0,
                    union_query.columns.private_sale_details_private_area,
                ),
            ]
        )

        query = (
            session.query(
                union_query.columns.private_sale_details_private_sales_id.label(
                    "private_sales_id"
                ),
                union_query.columns.private_sale_details_private_area.label(
                    "private_area"
                ),
                union_query.columns.private_sale_details_supply_area.label(
                    "supply_area"
                ),
                func.round(func.max(union_query.columns.avg_trade_price)).label(
                    "avg_trade_price"
                ),
                func.round(func.max(union_query.columns.avg_deposit_price)).label(
                    "avg_deposit_price"
                ),
                func.max(PrivateSaleAvgPriceModel.id).label(
                    "private_sale_avg_price_id"
                ),
                func.max(union_query.columns.max_trade_contract_date).label(
                    "max_trade_contract_date"
                ),
                func.max(union_query.columns.max_deposit_contract_date).label(
                    "max_deposit_contract_date"
                ),
            )
            .join(
                PrivateSaleAvgPriceModel,
                (
                    union_query.columns.private_sale_details_private_sales_id
                    == PrivateSaleAvgPriceModel.private_sales_id
                )
                & (pyoung_case == PrivateSaleAvgPriceModel.pyoung),
                isouter=True,
            )
            .group_by(
                union_query.columns.private_sale_details_private_sales_id,
                union_query.columns.private_sale_details_private_area,
                union_query.columns.private_sale_details_supply_area,
            )
        )

        query_set = query.all()

        if not query_set:
            return []

        return [
            RecentlyContractedEntity(
                private_sales_id=query.private_sales_id,
                private_area=query.private_area,
                supply_area=query.supply_area,
                avg_trade_price=query.avg_trade_price,
                avg_deposit_price=query.avg_deposit_price,
                private_sale_avg_price_id=query.private_sale_avg_price_id,
                max_trade_contract_date=query.max_trade_contract_date,
                max_deposit_contract_date=query.max_deposit_contract_date,
            )
            for query in query_set
        ]

    def make_pre_calc_target_private_sale_avg_prices_list(
        self, recent_infos: List[RecentlyContractedEntity], default_pyoung_dict: dict,
    ) -> Optional[Tuple[List[dict], List[dict]]]:
        if not recent_infos:
            return None

        avg_prices_update_list = list()
        avg_prices_create_list = list()

        for recent_info in recent_infos:
            # 평 계산시 겹치는 것들이 있기 때문에 정확도를 위해 supply_area 없을때는, private_area 로 평을 대체
            if not recent_info.supply_area and recent_info.supply_area != 0:
                pyoung_div = "S"  # {S}upply_area
                pyoung = recent_info.supply_area
            else:
                pyoung_div = "P"  # {P}rivate_area
                pyoung = recent_info.private_area

            default_pyoung = default_pyoung_dict.get(recent_info.private_sales_id)
            if not pyoung or not default_pyoung:
                continue

            avg_price_info = {
                "private_sales_id": recent_info.private_sales_id,
                "pyoung": pyoung,
                "default_trade_pyoung": default_pyoung["default_trade_pyoung"],
                "default_deposit_pyoung": default_pyoung["default_deposit_pyoung"],
                "pyoung_div": pyoung_div,
                "trade_price": recent_info.avg_trade_price,
                "deposit_price": recent_info.avg_deposit_price,
                "max_trade_contract_date": recent_info.max_trade_contract_date,
                "max_deposit_contract_date": recent_info.max_deposit_contract_date,
                "id": recent_info.private_sale_avg_price_id,
            }

            if recent_info.private_sale_avg_price_id:
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

    def get_default_pyoung_number_for_private_sale(self, target_ids: List[int]) -> dict:
        default_filters = list()

        default_filters.append(
            and_(
                PrivateSaleDetailModel.private_sales_id.in_(target_ids),
                PrivateSaleDetailModel.is_available == True,
            )
        )

        # 매매 거래 중 가장 건수가 많은 type 조회
        trade_sub_query = (
            session.query(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                func.row_number()
                .over(
                    partition_by=PrivateSaleDetailModel.private_sales_id,
                    order_by=and_(
                        func.count(PrivateSaleDetailModel.private_area).desc(),
                        func.max(PrivateSaleDetailModel.contract_date).desc(),
                    ),
                )
                .label("rank"),
            )
            .filter(*default_filters)
            .filter(
                PrivateSaleDetailModel.trade_type == RealTradeTypeEnum.TRADING.value
            )
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
            )
        ).subquery()

        trade_sub_q = aliased(trade_sub_query)

        trade_query = (
            session.query(trade_sub_q)
            .with_entities(
                trade_sub_q.c.private_sales_id.label("private_sales_id"),
                trade_sub_q.c.private_area.label("trade_private_area"),
                trade_sub_q.c.supply_area.label("trade_supply_area"),
                literal(0, None).label("deposit_private_area"),
                literal(0, None).label("deposit_supply_area"),
            )
            .group_by(
                trade_sub_q.c.private_sales_id,
                trade_sub_q.c.private_area,
                trade_sub_q.c.supply_area,
                trade_sub_q.c.rank,
            )
            .having(trade_sub_q.c.rank == 1)
        )

        # 전세 거래 중 가장 건수가 많은 type 조회
        deposit_sub_query = (
            session.query(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
                func.row_number()
                .over(
                    partition_by=PrivateSaleDetailModel.private_sales_id,
                    order_by=and_(
                        func.count(PrivateSaleDetailModel.private_area).desc(),
                        func.max(PrivateSaleDetailModel.contract_date).desc(),
                    ),
                )
                .label("rank"),
            )
            .filter(*default_filters)
            .filter(
                PrivateSaleDetailModel.trade_type
                == RealTradeTypeEnum.LONG_TERM_RENT.value
            )
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.private_area,
                PrivateSaleDetailModel.supply_area,
            )
        ).subquery()

        deposit_sub_q = aliased(deposit_sub_query)

        deposit_query = (
            session.query(deposit_sub_q)
            .with_entities(
                deposit_sub_q.c.private_sales_id.label("private_sales_id"),
                literal(0, None).label("trade_private_area"),
                literal(0, None).label("trade_supply_area"),
                deposit_sub_q.c.private_area.label("deposit_private_area"),
                deposit_sub_q.c.supply_area.label("deposit_supply_area"),
            )
            .group_by(
                deposit_sub_q.c.private_sales_id,
                deposit_sub_q.c.private_area,
                deposit_sub_q.c.supply_area,
                deposit_sub_q.c.rank,
            )
            .having(deposit_sub_q.c.rank == 1)
        )

        union_query = trade_query.union_all(deposit_query).subquery()
        final_query = (
            session.query(union_query)
            .with_entities(
                union_query.c.private_sales_id.label("private_sales_id"),
                func.max(union_query.c.trade_private_area).label("trade_private_area"),
                func.max(union_query.c.trade_supply_area).label("trade_supply_area"),
                func.max(union_query.c.deposit_private_area).label(
                    "deposit_private_area"
                ),
                func.max(union_query.c.deposit_supply_area).label(
                    "deposit_supply_area"
                ),
            )
            .group_by(union_query.c.private_sales_id)
        )

        query_set = final_query.all()

        default_pyoung_dict = dict()
        for query in query_set:
            # 현재 공급면적이 없는 것들이 많기 때문에 이럴 경우 전용면적을 계산식을 통해 입력
            # 평 계산시 겹치는 것들이 있기 때문에 정확도를 위해 supply_area 없을때는, private_area 로 평을 대체
            trade_default_pyoung = (
                query.trade_supply_area
                if not query.trade_supply_area and query.trade_supply_area != 0
                else query.trade_private_area
            )

            deposit_default_pyoung = (
                query.deposit_supply_area
                if not query.deposit_supply_area and query.deposit_supply_area != 0
                else query.deposit_private_area
            )

            default_pyoung_dict.update(
                {
                    query.private_sales_id: {
                        "default_trade_pyoung": trade_default_pyoung,
                        "default_deposit_pyoung": deposit_default_pyoung,
                    }
                }
            )

        return default_pyoung_dict

    def get_default_infos(self, public_sales_id: int) -> Optional[dict]:
        query = (
            session.query(
                PublicSaleDetailModel.supply_area, PublicSaleDetailModel.supply_price,
            )
            .filter(PublicSaleDetailModel.public_sales_id == public_sales_id)
            .order_by(PublicSaleDetailModel.general_household.desc(),)
        )

        query_set = query.first()

        if not query_set:
            return None
        elif query_set[0] == 0:
            return None

        return dict(supply_area=query_set[0], supply_price=query_set[1])

    def get_competition_and_min_score(self, public_sales_id: int) -> dict:
        sub_query = (
            session.query(PublicSaleDetailModel)
            .with_entities(
                PublicSaleDetailModel.public_sales_id,
                func.coalesce(
                    func.max(PublicSaleDetailModel.general_household), 0
                ).label("max_general_household"),
                func.coalesce(
                    func.sum(GeneralSupplyResultModel.applicant_num), 0
                ).label("sum_applicant_num"),
            )
            .join(PublicSaleDetailModel.general_supply_results)
            .filter(PublicSaleDetailModel.public_sales_id == public_sales_id)
            .filter(PublicSaleDetailModel.general_household > 0)
            .group_by(PublicSaleDetailModel.id,)
        ).subquery()

        min_point_query = (
            session.query(PublicSaleDetailModel)
            .with_entities(
                func.coalesce(func.min(GeneralSupplyResultModel.win_point), 0).label(
                    "min_win_point"
                )
            )
            .join(PublicSaleDetailModel.general_supply_results)
            .filter(PublicSaleDetailModel.public_sales_id == public_sales_id)
            .filter(GeneralSupplyResultModel.win_point > 0)
        ).subquery()

        base_query = (
            session.query(sub_query)
            .with_entities(
                func.coalesce(
                    func.round(
                        func.sum(sub_query.c.sum_applicant_num)
                        / func.sum(sub_query.c.max_general_household)
                    ),
                    0,
                ).label("avg_competition"),
                func.coalesce(func.min(min_point_query.c.min_win_point), 0).label(
                    "min_win_point"
                ),
            )
            .group_by(sub_query.c.public_sales_id)
        )

        query_set = base_query.first()
        if not query_set:
            return dict(avg_competition=None, min_score=None)

        return dict(avg_competition=query_set[0], min_score=query_set[1])

    def _is_exists_public_sale_avg_prices(
        self, public_sales_id: int, pyoung_number: int
    ) -> Optional[int]:
        query = (
            session.query(PublicSaleAvgPriceModel.id).filter(
                and_(
                    PublicSaleAvgPriceModel.public_sales_id == public_sales_id,
                    PublicSaleAvgPriceModel.pyoung == pyoung_number,
                )
            )
        ).first()

        if not query:
            return None
        return query.id

    def make_pre_calc_target_public_sale_avg_prices_list(
        self, public_sales_id: int, default_info: dict, competition_and_score_info: dict
    ) -> Optional[Tuple[List[dict], List[dict]]]:
        if not default_info:
            return None

        avg_prices_update_list = list()
        avg_prices_create_list = list()

        avg_price_info = {
            "public_sales_id": public_sales_id,
            "pyoung": HouseHelper.convert_area_to_pyoung(
                area=default_info["supply_area"]
            ),
            "default_pyoung": HouseHelper.convert_area_to_pyoung(
                area=default_info["supply_area"]
            ),
            "supply_price": default_info["supply_price"],
            "avg_competition": competition_and_score_info["avg_competition"],
            "min_score": competition_and_score_info["min_score"],
        }
        public_sale_avg_price_id = self._is_exists_public_sale_avg_prices(
            public_sales_id=avg_price_info["public_sales_id"],
            pyoung_number=avg_price_info["pyoung"],
        )

        if public_sale_avg_price_id:
            avg_price_info.update({"id": public_sale_avg_price_id})
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

    def get_common_query_object(self, yyyymm: int) -> Query:
        filters = list()
        today = get_server_timestamp().strftime("%Y-%m-%d")

        filters.append(PrivateSaleDetailModel.contract_ym >= yyyymm)

        filters.append(
            and_(
                PrivateSaleDetailModel.is_available == "True",
                func.to_char(PrivateSaleDetailModel.created_at, "YYYY-mm-dd") == today,
                PrivateSaleDetailModel.trade_type == "매매",
            )
            | and_(
                PrivateSaleDetailModel.is_available == "True",
                func.to_char(PrivateSaleDetailModel.updated_at, "YYYY-mm-dd") == today,
                PrivateSaleDetailModel.trade_type == "매매",
            )
            | and_(
                PrivateSaleDetailModel.is_available == "True",
                func.to_char(PrivateSaleDetailModel.created_at, "YYYY-mm-dd") == today,
                PrivateSaleDetailModel.trade_type == "전세",
            )
            | and_(
                PrivateSaleDetailModel.is_available == "True",
                func.to_char(PrivateSaleDetailModel.updated_at, "YYYY-mm-dd") == today,
                PrivateSaleDetailModel.trade_type == "전세",
            )
        )

        pyoung_case = case(
            [
                (
                    and_(
                        PrivateSaleDetailModel.supply_area != 0,
                        PrivateSaleDetailModel.supply_area != None,
                    ),
                    func.round(
                        PrivateSaleDetailModel.supply_area
                        / CalcPyoungEnum.CALC_VAR.value
                    ),
                ),
                (
                    PrivateSaleDetailModel.supply_area == 0,
                    func.round(
                        (
                            PrivateSaleDetailModel.private_area
                            * CalcPyoungEnum.TEMP_CALC_VAR.value
                        )
                        / CalcPyoungEnum.CALC_VAR.value
                    ),
                ),
            ]
        )

        query_cond1 = (
            session.query(PrivateSaleModel)
            .with_entities(
                PrivateSaleModel.real_estate_id,
                PrivateSaleModel.id,
                PrivateSaleModel.building_type,
                PrivateSaleDetailModel.trade_type,
                func.sum(pyoung_case).label("pyoung"),
                func.sum(PrivateSaleDetailModel.trade_price).label(
                    "apt_sum_trade_price"
                ),
                func.sum(PrivateSaleDetailModel.deposit_price).label(
                    "apt_sum_deposit_price"
                ),
                literal(0, Integer).label("op_sum_trade_price"),
                literal(0, Integer).label("op_sum_deposit_price"),
            )
            .join(
                PrivateSaleDetailModel,
                PrivateSaleModel.id == PrivateSaleDetailModel.private_sales_id,
            )
            .filter(*filters)
            .filter(PrivateSaleModel.building_type == "아파트")
            .group_by(
                PrivateSaleModel.real_estate_id,
                PrivateSaleModel.id,
                PrivateSaleModel.building_type,
                PrivateSaleDetailModel.trade_type,
            )
        )

        query_cond2 = (
            session.query(PrivateSaleModel)
            .with_entities(
                PrivateSaleModel.real_estate_id,
                PrivateSaleModel.id,
                PrivateSaleModel.building_type,
                PrivateSaleDetailModel.trade_type,
                func.sum(pyoung_case).label("pyoung"),
                literal(0, Integer).label("apt_sum_trade_price"),
                literal(0, Integer).label("apt_sum_deposit_price"),
                func.sum(PrivateSaleDetailModel.trade_price).label(
                    "op_sum_trade_price"
                ),
                func.sum(PrivateSaleDetailModel.deposit_price).label(
                    "op_sum_deposit_price"
                ),
            )
            .join(
                PrivateSaleDetailModel,
                PrivateSaleModel.id == PrivateSaleDetailModel.private_sales_id,
            )
            .filter(*filters)
            .filter(PrivateSaleModel.building_type == "오피스텔")
            .group_by(
                PrivateSaleModel.real_estate_id,
                PrivateSaleModel.id,
                PrivateSaleModel.building_type,
                PrivateSaleDetailModel.trade_type,
            )
        )

        union_query = query_cond1.union_all(query_cond2).subquery()
        sub_q = aliased(union_query)

        return sub_q

    def get_si_do_avg_price(self, sub_q: Query):
        query_cond3 = (
            session.query(RealEstateModel)
            .with_entities(
                RealEstateModel.si_do,
                func.max(RealEstateModel.front_legal_code).label("front_legal_code"),
                (
                    func.round(
                        func.sum(sub_q.c.apt_sum_trade_price) / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("apt_per_trade_price"),
                (
                    func.round(
                        func.sum(sub_q.c.apt_sum_deposit_price)
                        / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("apt_per_deposit_price"),
                (
                    func.round(
                        func.sum(sub_q.c.op_sum_trade_price) / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("op_per_trade_price"),
                (
                    func.round(
                        func.sum(sub_q.c.op_sum_deposit_price)
                        / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("op_per_deposit_price"),
            )
            .join(sub_q, RealEstateModel.id == sub_q.c.private_sales_real_estate_id)
            .group_by(
                RealEstateModel.si_do,
                sub_q.c.private_sale_details_trade_type,
                sub_q.c.private_sales_building_type,
            )
        ).subquery()

        final_sub_q = aliased(query_cond3)

        final_query = (
            session.query(final_sub_q)
            .with_entities(
                final_sub_q.c.si_do,
                func.substring(func.max(final_sub_q.c.front_legal_code), 1, 2).label(
                    "legal_code"
                ),
                func.sum(final_sub_q.c.apt_per_trade_price).label(
                    "apt_avg_trade_price"
                ),
                func.sum(final_sub_q.c.apt_per_deposit_price).label(
                    "apt_avg_deposit_price"
                ),
                func.sum(final_sub_q.c.op_per_trade_price).label("op_avg_trade_price"),
                func.sum(final_sub_q.c.op_per_deposit_price).label(
                    "op_avg_deposit_price"
                ),
            )
            .group_by(final_sub_q.c.si_do)
        )

        query_set = final_query.all()

        if not query_set:
            return []

        return self._make_administrative_calc_avg_entity(
            query_set=query_set, level=DivisionLevelEnum.LEVEL_1
        )

    def get_si_gun_gu_avg_price(self, sub_q: Query):
        query_cond3 = (
            session.query(RealEstateModel)
            .with_entities(
                RealEstateModel.si_do,
                RealEstateModel.si_gun_gu,
                RealEstateModel.front_legal_code,
                (
                    func.round(
                        func.sum(sub_q.c.apt_sum_trade_price) / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("apt_per_trade_price"),
                (
                    func.round(
                        func.sum(sub_q.c.apt_sum_deposit_price)
                        / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("apt_per_deposit_price"),
                (
                    func.round(
                        func.sum(sub_q.c.op_sum_trade_price) / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("op_per_trade_price"),
                (
                    func.round(
                        func.sum(sub_q.c.op_sum_deposit_price)
                        / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("op_per_deposit_price"),
            )
            .join(sub_q, RealEstateModel.id == sub_q.c.private_sales_real_estate_id)
            .group_by(
                RealEstateModel.si_do,
                RealEstateModel.si_gun_gu,
                RealEstateModel.front_legal_code,
                sub_q.c.private_sale_details_trade_type,
                sub_q.c.private_sales_building_type,
            )
        ).subquery()

        final_sub_q = aliased(query_cond3)

        final_query = (
            session.query(final_sub_q)
            .with_entities(
                final_sub_q.c.si_do,
                final_sub_q.c.si_gun_gu,
                final_sub_q.c.front_legal_code.label("legal_code"),
                func.sum(final_sub_q.c.apt_per_trade_price).label(
                    "apt_avg_trade_price"
                ),
                func.sum(final_sub_q.c.apt_per_deposit_price).label(
                    "apt_avg_deposit_price"
                ),
                func.sum(final_sub_q.c.op_per_trade_price).label("op_avg_trade_price"),
                func.sum(final_sub_q.c.op_per_deposit_price).label(
                    "op_avg_deposit_price"
                ),
            )
            .filter(
                and_(
                    final_sub_q.c.front_legal_code != "00000",
                    final_sub_q.c.si_do != "세종특별자치시",
                )
            )
            .group_by(
                final_sub_q.c.si_do,
                final_sub_q.c.si_gun_gu,
                final_sub_q.c.front_legal_code,
            )
        )

        query_set = final_query.all()

        if not query_set:
            return []

        return self._make_administrative_calc_avg_entity(
            query_set=query_set, level=DivisionLevelEnum.LEVEL_2
        )

    def get_dong_myun_avg_price(self, sub_q: Query):
        query_cond3 = (
            session.query(RealEstateModel)
            .with_entities(
                RealEstateModel.si_do,
                RealEstateModel.si_gun_gu,
                RealEstateModel.dong_myun,
                RealEstateModel.front_legal_code,
                RealEstateModel.back_legal_code,
                (
                    func.round(
                        func.sum(sub_q.c.apt_sum_trade_price) / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("apt_per_trade_price"),
                (
                    func.round(
                        func.sum(sub_q.c.apt_sum_deposit_price)
                        / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("apt_per_deposit_price"),
                (
                    func.round(
                        func.sum(sub_q.c.op_sum_trade_price) / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("op_per_trade_price"),
                (
                    func.round(
                        func.sum(sub_q.c.op_sum_deposit_price)
                        / func.sum(sub_q.c.pyoung)
                    )
                    * CalcPyoungEnum.AVG_DEFAULT_PYOUNG.value
                ).label("op_per_deposit_price"),
            )
            .join(sub_q, RealEstateModel.id == sub_q.c.private_sales_real_estate_id)
            .group_by(
                RealEstateModel.si_do,
                RealEstateModel.si_gun_gu,
                RealEstateModel.dong_myun,
                RealEstateModel.front_legal_code,
                RealEstateModel.back_legal_code,
                sub_q.c.private_sale_details_trade_type,
                sub_q.c.private_sales_building_type,
            )
        ).subquery()

        final_sub_q = aliased(query_cond3)

        final_query = (
            session.query(final_sub_q)
            .with_entities(
                final_sub_q.c.si_do,
                final_sub_q.c.si_gun_gu,
                final_sub_q.c.dong_myun,
                final_sub_q.c.front_legal_code.label("front_legal_code"),
                final_sub_q.c.back_legal_code.label("back_legal_code"),
                func.sum(final_sub_q.c.apt_per_trade_price).label(
                    "apt_avg_trade_price"
                ),
                func.sum(final_sub_q.c.apt_per_deposit_price).label(
                    "apt_avg_deposit_price"
                ),
                func.sum(final_sub_q.c.op_per_trade_price).label("op_avg_trade_price"),
                func.sum(final_sub_q.c.op_per_deposit_price).label(
                    "op_avg_deposit_price"
                ),
            )
            .filter(final_sub_q.c.front_legal_code != "00000")
            .group_by(
                final_sub_q.c.si_do,
                final_sub_q.c.si_gun_gu,
                final_sub_q.c.dong_myun,
                final_sub_q.c.front_legal_code,
                final_sub_q.c.back_legal_code,
            )
        )

        query_set = final_query.all()

        if not query_set:
            return []

        return self._make_administrative_calc_avg_entity(
            query_set=query_set, level=DivisionLevelEnum.LEVEL_3
        )

    def _make_administrative_calc_avg_entity(
        self, query_set: Query, level: Enum
    ) -> List[dict]:
        result = list()
        if level == DivisionLevelEnum.LEVEL_1:
            for query in query_set:
                result.append(
                    dict(
                        front_legal_code=query[1] + "000",
                        back_legal_code="00000",
                        apt_trade_price=query[2],
                        apt_deposit_price=query[3],
                        op_trade_price=query[4],
                        op_deposit_price=query[5],
                        public_sale_price=0,
                        level=level,
                    )
                )
        elif level == DivisionLevelEnum.LEVEL_2:
            for query in query_set:
                result.append(
                    dict(
                        front_legal_code=query[2],
                        back_legal_code="00000",
                        apt_trade_price=query[3],
                        apt_deposit_price=query[4],
                        op_trade_price=query[5],
                        op_deposit_price=query[6],
                        public_sale_price=0,
                        level=level,
                    )
                )
        else:
            for query in query_set:
                result.append(
                    dict(
                        front_legal_code=query[3],
                        back_legal_code=query[4],
                        apt_trade_price=query[5],
                        apt_deposit_price=query[6],
                        op_trade_price=query[7],
                        op_deposit_price=query[8],
                        public_sale_price=0,
                        level=level,
                    )
                )

        return result

    def set_administrative_division_id(
        self, result_list: List[dict]
    ) -> Tuple[List[dict], List[dict]]:
        failure_list = list()
        update_list = list()
        for result in result_list:
            query = (
                session.query(AdministrativeDivisionModel).filter_by(
                    front_legal_code=result["front_legal_code"],
                    back_legal_code=result["back_legal_code"],
                    level=result["level"],
                )
            ).first()

            if not query:
                failure_list.append(result)
                continue

            result["id"] = query.id
            update_list.append(result)
        return update_list, failure_list

    def update_avg_price_to_administrative_division(
        self, update_list: List[dict]
    ) -> None:
        try:
            session.bulk_update_mappings(
                AdministrativeDivisionModel,
                [update_info for update_info in update_list],
            )

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][update_avg_price_to_administrative_division] error : {e}"
            )
            raise UpdateFailErrorException

    def get_administrative_divisions_legal_code_info_all_list(
        self,
    ) -> List[AdministrativeDivisionLegalCodeEntity]:
        query = session.query(AdministrativeDivisionModel)

        query_set = query.all()

        return (
            [query.to_legal_code_entity() for query in query_set] if query_set else None
        )

    def get_real_estates_legal_code_info_should_update_list(
        self,
    ) -> List[RealEstateLegalCodeEntity]:
        filters = list()
        filters.append(
            and_(
                RealEstateModel.is_available == "True",
                RealEstateModel.front_legal_code == "00000",
                RealEstateModel.back_legal_code == "00000",
            )
        )
        query = session.query(RealEstateModel).filter(*filters)
        query_set = query.all()

        return (
            [query.to_legal_code_entity() for query in query_set] if query_set else None
        )

    def update_legal_code_to_real_estates(self, update_list: List[dict]) -> None:
        try:
            session.bulk_update_mappings(
                RealEstateModel, [update_info for update_info in update_list]
            )

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][update_legal_code_to_real_estates] error : {e}"
            )
            raise UpdateFailErrorException

    def get_target_list_of_public_sales(self) -> Optional[List[PublicSaleEntity]]:
        filters = list()
        filters.append(
            and_(
                PublicSaleModel.is_available == "True",
                PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE,
            )
        )
        query = (
            session.query(PublicSaleModel)
            .options(joinedload(PublicSaleModel.public_sale_photos))
            .options(joinedload(PublicSaleModel.public_sale_details))
            .options(joinedload("public_sale_details.public_sale_detail_photos"))
            .filter(*filters)
        )
        query_set = query.all()

        if not query_set:
            return None

        return [query.to_entity() for query in query_set] if query_set else None

    def get_target_list_of_public_sales_by_pk_list(
        self, target_ids: List[int]
    ) -> Optional[List[PublicSaleEntity]]:
        """
            for retry when failed batch
        """
        filters = list()
        filters.append(PublicSaleModel.id.in_(target_ids))
        query = (
            session.query(PublicSaleModel)
            .options(joinedload(PublicSaleModel.public_sale_photos))
            .options(joinedload(PublicSaleModel.public_sale_details))
            .options(joinedload("public_sale_details.public_sale_detail_photos"))
            .filter(*filters)
        )
        query_set = query.all()

        if not query_set:
            return None

        return [query.to_entity() for query in query_set] if query_set else None

    def insert_images_to_public_sale_photos(self, create_list: List[dict]) -> None:
        try:
            session.bulk_insert_mappings(
                PublicSalePhotoModel, [create_info for create_info in create_list]
            )

            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][insert_images_to_public_sale_photos] error : {e}"
            )
            raise NotUniqueErrorException

    def insert_images_to_public_sale_detail_photos(
        self, create_list: List[dict]
    ) -> None:
        try:
            session.bulk_insert_mappings(
                PublicSaleDetailPhotoModel, [create_info for create_info in create_list]
            )

            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][insert_images_to_public_sale_detail_photos] error : {e}"
            )
            raise NotUniqueErrorException

    def get_recent_public_sale_photos(self):
        query = (
            session.query(PublicSalePhotoModel)
            .order_by(PublicSalePhotoModel.id.desc())
            .limit(1)
        )
        query_set = query.first()
        if not query_set:
            return None
        return query_set.to_entity()

    def get_recent_public_sale_detail_photos(self):
        query = (
            session.query(PublicSaleDetailPhotoModel)
            .order_by(PublicSaleDetailPhotoModel.id.desc())
            .limit(1)
        )
        query_set = query.first()
        if not query_set:
            return None
        return query_set.to_entity()

    def get_main_recent_public_info_list(self) -> Optional[list]:
        filters = list()
        filters.append(
            and_(
                PublicSaleModel.is_available == "True",
                PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE.value,
            )
        )

        query = (
            session.using_bind("read_only")
            .query(PublicSaleModel)
            .with_entities(
                PublicSaleModel.id.label("id"),
                PublicSaleModel.name.label("name"),
                PublicSaleModel.offer_date.label("offer_date"),
                PublicSaleModel.subscription_end_date.label("subscription_end_date"),
                RealEstateModel.si_do.label("si_do"),
                func.coalesce(PublicSalePhotoModel.path, None).label(
                    "public_sale_photo"
                ),
            )
            .join(
                PublicSalePhotoModel,
                (PublicSalePhotoModel.public_sales_id == PublicSaleModel.id)
                & (PublicSalePhotoModel.is_thumbnail == "True")
                & (PublicSalePhotoModel.seq == 0),
                isouter=True,
            )
            .join(
                RealEstateModel,
                (RealEstateModel.id == PublicSaleModel.real_estate_id)
                & (RealEstateModel.is_available == "True"),
            )
            .filter(*filters)
            .order_by(PublicSaleModel.subscription_end_date.desc())
            .limit(12)
        )

        query_set = query.all()

        if not query_set:
            return None

        return query_set

    def get_main_recent_public_info_list_without_image(self) -> Optional[list]:
        filters = list()
        filters.append(
            and_(
                PublicSaleModel.is_available == "True",
                PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE.value,
            )
        )

        query = (
            session.query(PublicSaleModel)
            .options(joinedload(PublicSaleModel.real_estates))
            .filter(*filters)
            .order_by(PublicSaleModel.subscription_end_date.desc())
            .limit(12)
        )

        query_set = query.all()

        if not query_set:
            return None

        return query_set

    def get_near_houses_bounding(
        self, bounding_filter: _FunctionGenerator
    ) -> Optional[List[NearHouseEntity]]:
        filters = list()
        pyoung_filters = list()
        private_filters = list()

        filters.append(bounding_filter)
        filters.append(RealEstateModel.is_available == "True",)

        private_filters.append(
            and_(
                PrivateSaleModel.is_available == "True",
                PrivateSaleModel.building_type == BuildTypeEnum.APARTMENT.value,
                PrivateSaleModel.trade_status
                >= PrivateSaleContractStatusEnum.LONG_AGO.value,
            )
        )

        pyoung_filters.append(
            PrivateSaleAvgPriceModel.default_trade_pyoung
            == PrivateSaleAvgPriceModel.pyoung
        )

        pyoung_case = case(
            [
                (
                    PrivateSaleAvgPriceModel.pyoung_div == "S",
                    func.round(
                        PrivateSaleAvgPriceModel.pyoung / CalcPyoungEnum.CALC_VAR.value
                    ),
                )
            ],
            else_=func.round(
                (PrivateSaleAvgPriceModel.pyoung * CalcPyoungEnum.TEMP_CALC_VAR.value)
                / CalcPyoungEnum.CALC_VAR.value
            ),
        )

        real_estate_sub_query = (
            session.using_bind("read_only").query(RealEstateModel).filter(*filters)
        ).subquery()

        private_trade_query = (
            session.using_bind("read_only")
            .query(real_estate_sub_query)
            .with_entities(
                real_estate_sub_query.c.id.label("real_estate_id"),
                real_estate_sub_query.c.jibun_address.label("jibun_address"),
                real_estate_sub_query.c.road_address.label("road_address"),
                real_estate_sub_query.c.coordinates.ST_Y().label("latitude"),
                real_estate_sub_query.c.coordinates.ST_X().label("longitude"),
                PrivateSaleModel.id.label("id"),
                PrivateSaleModel.building_type.label("building_type"),
                PrivateSaleModel.name.label("name"),
                PrivateSaleModel.trade_status.label("trade_status"),
                pyoung_case.label("trade_pyoung"),
                PrivateSaleAvgPriceModel.trade_price.label("trade_price"),
            )
            .join(
                PrivateSaleModel,
                PrivateSaleModel.real_estate_id == real_estate_sub_query.c.id,
            )
            .join(
                PrivateSaleAvgPriceModel,
                PrivateSaleAvgPriceModel.private_sales_id == PrivateSaleModel.id,
            )
            .filter(*private_filters, *pyoung_filters)
        )

        query_set = private_trade_query.all()

        if not query_set:
            return None

        near_houses_entities = list()

        for query in query_set:
            near_houses_entities.append(
                NearHouseEntity(
                    real_estate_id=query.real_estate_id,
                    jibun_address=query.jibun_address,
                    road_address=query.road_address,
                    latitude=query.latitude,
                    longitude=query.longitude,
                    private_sales_id=query.id,
                    building_type=query.building_type,
                    name=query.name,
                    trade_status=query.trade_status,
                    trade_pyoung=None
                    if query.trade_pyoung == 0
                    else query.trade_pyoung,
                    trade_price=None if query.trade_price == 0 else query.trade_price,
                )
            )

        return near_houses_entities

    def get_update_status_target_of_private_sale_details(
        self, private_sales_ids: List[int]
    ) -> List[UpdateContractStatusTargetEntity]:
        filters = list()
        filters.append(
            and_(
                PrivateSaleDetailModel.private_sales_id.in_(private_sales_ids),
                PrivateSaleDetailModel.is_available == "True",
            )
        )

        query_cond_1 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_sales_id,
                func.to_char(
                    func.to_date(
                        func.max(PrivateSaleDetailModel.contract_date), "YYYYMMDD"
                    ),
                    "YYYYMMDD",
                ).label("max_contract_date"),
                func.to_char(
                    (
                        func.to_date(
                            func.max(PrivateSaleDetailModel.contract_date), "YYYYMMDD"
                        )
                        - timedelta(days=93)
                    ),
                    "YYYYMMDD",
                ).label("min_contract_date"),
                PrivateSaleDetailModel.trade_type,
            )
            .filter(*filters)
            .filter(PrivateSaleDetailModel.trade_type == "매매")
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.trade_type,
            )
        )

        query_cond_2 = (
            session.query(PrivateSaleDetailModel)
            .with_entities(
                PrivateSaleDetailModel.private_sales_id,
                func.to_char(
                    func.to_date(
                        func.max(PrivateSaleDetailModel.contract_date), "YYYYMMDD"
                    ),
                    "YYYYMMDD",
                ).label("max_contract_date"),
                func.to_char(
                    (
                        func.to_date(
                            func.max(PrivateSaleDetailModel.contract_date), "YYYYMMDD"
                        )
                        - timedelta(days=93)
                    ),
                    "YYYYMMDD",
                ).label("min_contract_date"),
                PrivateSaleDetailModel.trade_type,
            )
            .filter(*filters)
            .filter(PrivateSaleDetailModel.trade_type == "전세")
            .group_by(
                PrivateSaleDetailModel.private_sales_id,
                PrivateSaleDetailModel.trade_type,
            )
        )

        query = query_cond_1.union_all(query_cond_2)

        query_set = query.all()

        if not query_set:
            return []

        return [
            UpdateContractStatusTargetEntity(
                private_sales_id=query[0],
                max_contract_date=query[1],
                min_contract_date=query[2],
                trade_type=query[3],
            )
            for query in query_set
        ]

    def bulk_update_private_sales(self, update_list: List[dict]) -> None:
        try:
            session.bulk_update_mappings(
                PrivateSaleModel, [update_info for update_info in update_list],
            )

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"[HouseRepository][bulk_update_private_sales] error : {e}")
            raise UpdateFailErrorException

    def get_private_sales_all_id_list(self,) -> Optional[List[int]]:
        """
            연립다세대 제외
        """
        target_ids = list()
        filters = list()
        today = get_server_timestamp().strftime("%Y-%m-%d")

        filters.append(
            and_(
                PrivateSaleModel.is_available == "True",
                PrivateSaleModel.building_type != BuildTypeEnum.ROW_HOUSE.value,
                func.to_char(PrivateSaleModel.created_at, "YYYY-mm-dd") == today,
            )
            | and_(
                PrivateSaleModel.is_available == "True",
                PrivateSaleModel.building_type != BuildTypeEnum.ROW_HOUSE.value,
                func.to_char(PrivateSaleModel.updated_at, "YYYY-mm-dd") == today,
            )
        )
        query = session.query(PrivateSaleModel).filter(*filters)

        query_set = query.all()

        if not query_set:
            return None

        for query in query_set:
            if query.id:
                target_ids.append(query.id)

        return target_ids

    def get_private_sales_have_real_estates_both_public_and_private(
        self, real_estates_ids: List[int]
    ) -> Optional[List]:
        filters = list()
        filters.append(and_(PrivateSaleModel.real_estate_id.in_(real_estates_ids),))
        query = (
            session.query(PrivateSaleModel)
            .options(joinedload(PrivateSaleModel.private_sale_details))
            .filter(*filters)
        )
        query_set = query.all()

        if not query_set:
            return None

        return [query.to_entity() for query in query_set] if query_set else None

    def bulk_update_public_sales(self, update_list: List[dict]) -> None:
        try:
            session.bulk_update_mappings(
                PublicSaleModel, [update_info for update_info in update_list],
            )

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"[HouseRepository][bulk_update_public_sales] error : {e}")
            raise UpdateFailErrorException

    def get_recent_private_sales(self):
        query = (
            session.query(PrivateSaleModel)
            .options(joinedload(PrivateSaleModel.private_sale_details))
            .order_by(PrivateSaleModel.id.desc())
            .limit(1)
        )
        query_set = query.first()
        if not query_set:
            return None
        return query_set.to_entity()

    def bulk_create_private_sale(self, create_list: List[dict]) -> None:
        failed_pk_list = list()
        try:
            session.bulk_insert_mappings(
                PrivateSaleModel, [create_info for create_info in create_list]
            )

            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(f"[HouseRepository][bulk_create_private_sale] error : {e}")
            for entry in create_list:
                failed_pk_list.append(entry["id"])
            logger.info(
                f"[HouseRepository][bulk_create_private_sale]-failed_list: {failed_pk_list})"
            )
            raise NotUniqueErrorException

    def get_real_estates_have_both_public_and_private(
        self, real_estates_ids: List[int]
    ) -> Optional[List[CheckIdsRealEstateEntity]]:
        result = list()
        filters = list()
        filters.append(RealEstateModel.id.in_(real_estates_ids),)

        query = (
            session.query(RealEstateModel)
            .with_entities(
                RealEstateModel.id.label("real_estate_id"),
                PrivateSaleModel.id.label("private_sales_id"),
                PublicSaleModel.id.label("public_sales_id"),
                PublicSaleModel.move_in_year.label("move_in_year"),
                PublicSaleModel.move_in_month.label("move_in_month"),
                PublicSaleModel.supply_household.label("supply_household"),
                PublicSaleModel.construct_company.label("construct_company"),
            )
            .join(
                PrivateSaleModel, PrivateSaleModel.real_estate_id == RealEstateModel.id
            )
            .join(PublicSaleModel, PublicSaleModel.real_estate_id == RealEstateModel.id)
            .filter(*filters)
        )
        query_set = query.all()

        if not query_set:
            return None

        for query in query_set:
            result.append(
                CheckIdsRealEstateEntity(
                    real_estate_id=query.real_estate_id,
                    public_sales_id=query.public_sales_id,
                    private_sales_id=query.private_sales_id,
                    move_in_year=HouseHelper().add_move_in_year_and_move_in_month_to_str(
                        move_in_year=query.move_in_year,
                        move_in_month=query.move_in_month,
                    )
                    if query.move_in_year and query.move_in_month
                    else None,
                    supply_household=query.supply_household,
                    construct_company=query.construct_company
                    if query.construct_company
                    else None,
                )
            )

        return result

    def get_target_list_of_upsert_public_sale_avg_prices(self) -> Optional[List[int]]:
        filters = list()
        today = get_server_timestamp().strftime("%Y-%m-%d")

        filters.append(
            and_(
                PublicSaleModel.is_available == "True",
                PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE,
                func.to_char(PublicSaleModel.created_at, "YYYY-mm-dd") == today,
            )
            | and_(
                PublicSaleModel.is_available == "True",
                PublicSaleModel.rent_type == RentTypeEnum.PRE_SALE,
                func.to_char(PublicSaleModel.updated_at, "YYYY-mm-dd") == today,
            )
        )
        query = (
            session.query(PublicSaleModel)
            .join(
                PublicSaleDetailModel,
                (PublicSaleDetailModel.public_sales_id == PublicSaleModel.id)
                & (PublicSaleDetailModel.supply_area != 0)
                & (PublicSaleDetailModel.area_type != None),
            )
            .filter(*filters)
            .group_by(PublicSaleModel.id)
        )
        query_set = query.all()

        if not query_set:
            return None

        target_ids = list()
        for query in query_set:
            if query.id:
                target_ids.append(query.id)

        return target_ids

    def get_target_of_upsert_private_sale_avg_prices(self,) -> Optional[List[int]]:
        """
            연립다세대 제외
        """
        target_ids = list()
        filters = list()
        today = get_server_timestamp().strftime("%Y-%m-%d")
        filters.append(
            and_(
                PrivateSaleModel.is_available == "True",
                PrivateSaleModel.building_type != BuildTypeEnum.ROW_HOUSE.value,
                func.to_char(PrivateSaleModel.created_at, "YYYY-mm-dd") == today,
            )
            | and_(
                PrivateSaleModel.is_available == "True",
                PrivateSaleModel.building_type != BuildTypeEnum.ROW_HOUSE.value,
                func.to_char(PrivateSaleModel.updated_at, "YYYY-mm-dd") == today,
            )
        )
        query = session.query(PrivateSaleModel).filter(*filters)

        query_set = query.all()
        if not query_set:
            return None

        for query in query_set:
            if query.id:
                target_ids.append(query.id)

        return target_ids

    def is_exists_public_sale_photos(self, public_sales_id: int) -> bool:
        query = session.query(
            exists().where(PublicSalePhotoModel.public_sales_id == public_sales_id)
        )
        if query.scalar():
            return True
        return False

    # todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
    def get_target_of_add_to_supply_area(self,) -> Optional[List[AddSupplyAreaEntity]]:
        """
            연립다세대 제외
        """
        target_list = list()
        filters = list()
        today = get_server_timestamp().strftime("%Y-%m-%d")
        filters.append(
            and_(
                RealEstateModel.is_available == "True",
                PrivateSaleModel.is_available == "True",
                PrivateSaleModel.building_type != BuildTypeEnum.ROW_HOUSE.value,
                # func.to_char(PrivateSaleModel.created_at, "YYYY-mm-dd") == today,
            )
            # | and_(
            #     PrivateSaleModel.is_available == "True",
            #     PrivateSaleModel.building_type != BuildTypeEnum.ROW_HOUSE.value,
            #     func.to_char(PrivateSaleModel.updated_at, "YYYY-mm-dd") == today,
            # )
        )
        query = (
            session.query(RealEstateModel)
            .with_entities(
                RealEstateModel.front_legal_code,
                RealEstateModel.back_legal_code,
                RealEstateModel.land_number,
                RealEstateModel.id,
                RealEstateModel.name,
                PrivateSaleModel.id.label("private_sales_id"),
                PrivateSaleModel.name.label("private_sale_name"),
                RealEstateModel.jibun_address,
                RealEstateModel.road_address,
            )
            .join(
                PrivateSaleModel, RealEstateModel.id == PrivateSaleModel.real_estate_id
            )
            .filter(*filters)
            .order_by(RealEstateModel.id)
            .limit(5000)
        )

        print("-----------------------")
        RawQueryHelper.print_raw_query(query)
        query_set = query.all()

        if not query_set:
            return None

        for query in query_set:
            target_list.append(
                AddSupplyAreaEntity(
                    req_front_legal_code=query.front_legal_code,
                    req_back_legal_code=query.back_legal_code,
                    req_land_number=query.land_number,
                    req_real_estate_id=query.id,
                    req_real_estate_name=query.name,
                    req_private_sales_id=query.private_sales_id,
                    req_private_sale_name=query.private_sale_name,
                    req_jibun_address=query.jibun_address,
                    req_road_address=query.road_address,
                )
            )

        return target_list

    # todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
    def create_temp_supply_area_api(self, create_list: List[dict]) -> None:
        try:
            session.bulk_insert_mappings(
                TempSupplyAreaApiModel, [create_info for create_info in create_list]
            )

            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(f"[HouseRepository][create_temp_supply_area_api] error : {e}")
            raise NotUniqueErrorException

    # todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
    def create_summary_failure_list_to_temp_summary(
        self, create_list: List[dict]
    ) -> None:
        try:
            session.bulk_insert_mappings(
                TempSummarySupplyAreaApiModel,
                [create_info for create_info in create_list],
            )

            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][create_temp_summary_supply_area_api] error : {e}"
            )
            raise NotUniqueErrorException

    # todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
    def create_summary_success_list_to_temp_summary(self) -> None:
        create_list = list()

        try:
            sub_query = (
                session.query(TempSupplyAreaApiModel)
                .with_entities(
                    TempSupplyAreaApiModel.req_real_estate_id,
                    TempSupplyAreaApiModel.req_real_estate_name,
                    TempSupplyAreaApiModel.req_private_sales_id,
                    TempSupplyAreaApiModel.req_private_sale_name,
                    func.coalesce(func.sum(TempSupplyAreaApiModel.resp_area), 0).label(
                        "supply_area"
                    ),
                    func.max(TempSupplyAreaApiModel.resp_area).label("private_area"),
                )
                .group_by(
                    TempSupplyAreaApiModel.req_real_estate_id,
                    TempSupplyAreaApiModel.req_real_estate_name,
                    TempSupplyAreaApiModel.req_private_sales_id,
                    TempSupplyAreaApiModel.req_private_sale_name,
                    TempSupplyAreaApiModel.resp_name,
                    TempSupplyAreaApiModel.resp_dong_nm,
                    TempSupplyAreaApiModel.resp_ho_nm,
                )
            ).subquery()

            query = (
                session.query(sub_query)
                .with_entities(
                    sub_query.c.req_real_estate_id,
                    func.max(sub_query.c.req_real_estate_name).label(
                        "req_real_estate_name"
                    ),
                    sub_query.c.req_private_sales_id,
                    func.max(sub_query.c.req_private_sale_name).label(
                        "req_private_sale_name"
                    ),
                    sub_query.c.private_area,
                    sub_query.c.supply_area,
                )
                .group_by(
                    sub_query.c.req_real_estate_id,
                    sub_query.c.req_private_sales_id,
                    sub_query.c.private_area,
                    sub_query.c.supply_area,
                )
                .order_by(
                    sub_query.c.req_real_estate_id,
                    sub_query.c.req_private_sales_id,
                    sub_query.c.private_area,
                )
            )

            query_set = query.all()

            for query in query_set:
                create_list.append(
                    dict(
                        real_estate_id=query.req_real_estate_id,
                        real_estate_name=query.req_real_estate_name,
                        private_sales_id=query.req_private_sales_id,
                        private_sale_name=query.req_private_sale_name,
                        private_area=query.private_area,
                        supply_area=MathHelper.round(query.supply_area, 2),
                        success_yn=True,
                    )
                )

            session.bulk_insert_mappings(
                TempSummarySupplyAreaApiModel,
                [create_info for create_info in create_list],
            )

            session.commit()

        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][create_temp_summary_supply_area_api] error : {e}"
            )
            raise NotUniqueErrorException
