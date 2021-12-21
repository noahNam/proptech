import re
from http import HTTPStatus
from typing import Union, List, Optional, Dict

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
from app.extensions.utils.house_helper import HouseHelper
from app.extensions.utils.image_helper import S3Helper
from app.extensions.utils.report_helper import ReportHelper
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.banner.entity.banner_entity import (
    BannerEntity,
    ButtonLinkEntity,
)
from core.domains.banner.enum import BannerTopicEnum
from core.domains.house.dto.house_dto import (
    CoordinatesRangeDto,
    GetHousePublicDetailDto,
    GetCalendarInfoDto,
    GetSearchHouseListDto,
    BoundingWithinRadiusDto,
    SectionTypeDto,
    GetHouseMainDto,
    GetHousePublicNearPrivateSalesDto,
    UpdateRecentViewListDto,
)
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.entity.house_entity import (
    GetRecentViewListEntity,
    GetMainPreSubscriptionEntity,
    GetHouseMainEntity,
    SimpleCalendarInfoEntity,
    InterestHouseListEntity,
    MainRecentPublicInfoEntity,
    HousePublicDetailEntity,
    MapSearchEntity,
    BoundingRealEstateEntity,
    PublicSalePhotoEntity,
    PublicSaleDetailEntity,
)
from core.domains.house.enum.house_enum import (
    BoundingLevelEnum,
    HouseTypeEnum,
    SearchTypeEnum,
    SectionType,
    BoundingDegreeEnum,
    BoundingPrivateTypeEnum,
    BoundingPublicTypeEnum,
    CapitalAreaEnum,
    HousingCategoryEnum,
    ButtonSectionType,
)
from core.domains.house.repository.house_repository import HouseRepository
from core.domains.house.schema.house_schema import (
    PublicSaleDetailBaseSchema,
    HousePublicDetailSchema,
)
from core.domains.report.entity.report_entity import (
    TicketUsageResultEntity,
    TicketUsageResultForHousePublicDetailEntity,
)
from core.domains.report.enum import ReportTopicEnum
from core.domains.report.enum.report_enum import TicketUsageTypeEnum
from core.domains.user.dto.user_dto import RecentlyViewDto, GetUserDto
from core.domains.user.enum import UserTopicEnum
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class HouseBaseUseCase:
    @inject.autoparams()
    def __init__(self, house_repo: HouseRepository):
        self._house_repo = house_repo

    def _get_banner_list(self, section_type: int) -> List[BannerEntity]:
        send_message(
            topic_name=BannerTopicEnum.GET_BANNER_LIST, section_type=section_type
        )
        return get_event_object(topic_name=BannerTopicEnum.GET_BANNER_LIST)

    def _get_button_link_list(self, section_type: int) -> List[ButtonLinkEntity]:
        send_message(
            topic_name=BannerTopicEnum.GET_BUTTON_LINK_LIST, section_type=section_type
        )
        return get_event_object(topic_name=BannerTopicEnum.GET_BUTTON_LINK_LIST)


class UpsertInterestHouseUseCase(HouseBaseUseCase):
    def execute(
        self, dto: UpsertInterestHouseDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # FE 요청으로 단순 upsert -> 찜한 내역 response 보내주는 것으로 변경
        interest_house_id: int = self._house_repo.update_interest_house(dto=dto)
        if not interest_house_id:
            self._house_repo.create_interest_house(dto=dto)

        result: Optional[InterestHouseListEntity] = self._house_repo.get_interest_house(
            user_id=dto.user_id, house_id=dto.house_id
        )

        if not result:
            return UseCaseFailureOutput(
                type="interest_house",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        return UseCaseSuccessOutput(value=result)


class BoundingUseCase(HouseBaseUseCase):
    def execute(
        self, dto: CoordinatesRangeDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        """
            <dto.level condition>
                level 16 이상 : 매물 쿼리
                level 15 이하 : 행정구역별 평균 가격 쿼리
                level 값 조절시 bounding_view()의 presenter 선택 조건 고려해야 합니다.
        """
        if not (dto.start_x and dto.start_y and dto.end_x and dto.end_y and dto.level):
            return UseCaseFailureOutput(
                type="map_coordinates",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )
        # dto.level range check
        if (
            dto.level < BoundingLevelEnum.MIN_NAVER_MAP_API_ZOOM_LEVEL.value
            or dto.level > BoundingLevelEnum.MAX_NAVER_MAP_API_ZOOM_LEVEL.value
        ):
            return UseCaseFailureOutput(
                type="level",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )

        # dto.private_type check
        if dto.private_type not in BoundingPrivateTypeEnum.list():
            return UseCaseFailureOutput(
                type="private_type",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )

        # dto.public_type check
        if (
            dto.public_type < BoundingPublicTypeEnum.NOTHING.value
            or BoundingPublicTypeEnum.ALL_PRE_SALE.value < dto.public_type
        ):
            return UseCaseFailureOutput(
                type="public_type",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )

        private_filters = self._house_repo.get_bounding_private_type_filter(
            private_type=dto.private_type
        )
        public_filters = self._house_repo.get_bounding_public_type_filter(
            public_type=dto.public_type
        )

        # dto.level condition
        if dto.level >= BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value:
            bounding_filter = self._house_repo.get_bounding_filter_with_two_points(
                dto=dto
            )
            bounding_entities_list: Union[
                List[BoundingRealEstateEntity], List
            ] = self._house_repo.get_bounding(
                bounding_filter=bounding_filter,
                private_filters=private_filters,
                public_filters=public_filters,
                public_status_filters=dto.public_status,
                include_private=dto.include_private,
                min_area=dto.min_area,
                max_area=dto.max_area,
            )
        else:
            bounding_entities_list = self._house_repo.get_administrative_divisions(
                dto=dto
            )

        return UseCaseSuccessOutput(value=bounding_entities_list)


class GetHousePublicDetailUseCase(HouseBaseUseCase):
    def _sort_public_sale_photos(self, photos: List[PublicSalePhotoEntity]):
        if not photos:
            return None
        photos.sort(key=lambda obj: obj.seq, reverse=False)

    def _sort_public_sale_detail_photos(self, details: List[PublicSaleDetailEntity]):
        if not details:
            return None

        end = len(details) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                # 102A, 84A str로 비교시 84A가 크기 때문에 숫자로 비교
                number1 = "".join(re.findall("\d+", details[i].area_type)[0])
                number2 = "".join(re.findall("\d+", details[i + 1].area_type)[0])

                if int(number1) > int(number2):
                    details[i], details[i + 1] = (
                        details[i + 1],
                        details[i],
                    )
                    last_swap = i
            end = last_swap

        end = len(details) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                # 위의 숫자기반 정렬을 알파벳 순으로 다시 재정렬
                word1 = "".join(re.findall("[a-zA-Z]+", details[i].area_type))
                word2 = "".join(re.findall("[a-zA-Z]+", details[i + 1].area_type))

                number1 = "".join(re.findall("\d+", details[i].area_type)[0])
                number2 = "".join(re.findall("\d+", details[i + 1].area_type)[0])

                if (number1 == number2) and (word1 > word2):
                    details[i], details[i + 1] = (
                        details[i + 1],
                        details[i],
                    )
                    last_swap = i
            end = last_swap

    def _is_private_category(self, housing_category: str) -> bool:
        """
            민영분양 -> return true
            공공분양 -> return false
        """
        if housing_category == HousingCategoryEnum.PRIVATE.value:
            return True
        return False

    def _make_response_schema(
        self,
        house_public_detail_entity: HousePublicDetailEntity,
        house_applicants_dict: Dict,
        public_sale_detail_dict: Dict,
    ):
        """
            For_client - 원하는 형태로 Response 형태 변형
        """
        public_sale_photos = None
        if house_public_detail_entity.public_sales.public_sale_photos:
            house_public_detail_entity.public_sales.public_sale_photos.sort(
                key=lambda obj: obj.seq, reverse=False
            )
            public_sale_photos = [
                public_sale_photo.path
                for public_sale_photo in house_public_detail_entity.public_sales.public_sale_photos
            ]

        public_sales = PublicSaleDetailBaseSchema(
            id=house_public_detail_entity.public_sales.id,
            real_estate_id=house_public_detail_entity.public_sales.real_estate_id,
            name=house_public_detail_entity.public_sales.name,
            region=house_public_detail_entity.public_sales.region,
            housing_category=house_public_detail_entity.public_sales.housing_category,
            rent_type=house_public_detail_entity.public_sales.rent_type,
            trade_type=house_public_detail_entity.public_sales.trade_type,
            construct_company=house_public_detail_entity.public_sales.construct_company,
            supply_household=house_public_detail_entity.public_sales.supply_household,
            is_available=house_public_detail_entity.public_sales.is_available,
            offer_date=house_public_detail_entity.public_sales.offer_date,
            offer_notice_url=house_public_detail_entity.public_sales.offer_notice_url,
            subscription_start_date=house_public_detail_entity.public_sales.subscription_start_date,
            subscription_end_date=house_public_detail_entity.public_sales.subscription_end_date,
            status=house_public_detail_entity.public_sales.status,
            special_supply_date=house_public_detail_entity.public_sales.special_supply_date,
            special_supply_etc_date=house_public_detail_entity.public_sales.special_supply_etc_date,
            special_etc_gyeonggi_date=house_public_detail_entity.public_sales.special_etc_gyeonggi_date,
            first_supply_date=house_public_detail_entity.public_sales.first_supply_date,
            first_supply_etc_date=house_public_detail_entity.public_sales.first_supply_etc_date,
            first_etc_gyeonggi_date=house_public_detail_entity.public_sales.first_etc_gyeonggi_date,
            second_supply_date=house_public_detail_entity.public_sales.second_supply_date,
            second_supply_etc_date=house_public_detail_entity.public_sales.second_supply_etc_date,
            second_etc_gyeonggi_date=house_public_detail_entity.public_sales.second_etc_gyeonggi_date,
            notice_winner_date=house_public_detail_entity.public_sales.notice_winner_date,
            contract_start_date=house_public_detail_entity.public_sales.contract_start_date,
            contract_end_date=house_public_detail_entity.public_sales.contract_end_date,
            move_in_year=house_public_detail_entity.public_sales.move_in_year,
            move_in_month=house_public_detail_entity.public_sales.move_in_month,
            min_down_payment=house_public_detail_entity.public_sales.min_down_payment,
            max_down_payment=house_public_detail_entity.public_sales.max_down_payment,
            down_payment_ratio=house_public_detail_entity.public_sales.down_payment_ratio,
            reference_url=house_public_detail_entity.public_sales.reference_url,
            total_household=house_public_detail_entity.public_sales.total_household,
            total_park_number=house_public_detail_entity.public_sales.total_park_number,
            top_floor=house_public_detail_entity.public_sales.top_floor,
            dong_number=house_public_detail_entity.public_sales.dong_number,
            contract_amount=house_public_detail_entity.public_sales.contract_amount,
            middle_amount=house_public_detail_entity.public_sales.middle_amount,
            remain_amount=house_public_detail_entity.public_sales.remain_amount,
            sale_limit=house_public_detail_entity.public_sales.sale_limit,
            public_sale_details=public_sale_detail_dict.get("public_sale_details")
            if public_sale_detail_dict
            else None,
        )

        return HousePublicDetailSchema(
            id=house_public_detail_entity.id,
            name=house_public_detail_entity.name,
            road_address=house_public_detail_entity.road_address,
            jibun_address=house_public_detail_entity.jibun_address,
            si_do=house_public_detail_entity.si_do,
            si_gun_gu=house_public_detail_entity.si_gun_gu,
            dong_myun=house_public_detail_entity.dong_myun,
            ri=house_public_detail_entity.ri,
            road_name=house_public_detail_entity.road_name,
            road_number=house_public_detail_entity.road_number,
            land_number=house_public_detail_entity.land_number,
            is_available=house_public_detail_entity.is_available,
            latitude=house_public_detail_entity.latitude,
            longitude=house_public_detail_entity.longitude,
            is_like=house_public_detail_entity.is_like,
            min_pyoung_number=house_public_detail_entity.min_pyoung_number,
            max_pyoung_number=house_public_detail_entity.max_pyoung_number,
            min_supply_area=house_public_detail_entity.min_supply_area,
            max_supply_area=house_public_detail_entity.max_supply_area,
            avg_supply_price=house_public_detail_entity.avg_supply_price,
            min_supply_price=house_public_detail_entity.min_supply_price,
            max_supply_price=house_public_detail_entity.max_supply_price,
            supply_price_per_pyoung=house_public_detail_entity.supply_price_per_pyoung,
            min_acquisition_tax=house_public_detail_entity.min_acquisition_tax,
            max_acquisition_tax=house_public_detail_entity.max_acquisition_tax,
            public_sales=public_sales,
            public_sale_photos=public_sale_photos,
            button_links=house_public_detail_entity.button_links,
            ticket_usage_results=house_public_detail_entity.ticket_usage_results,
            house_applicants=house_applicants_dict,
        )

    def execute(
        self, dto: GetHousePublicDetailDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not self._house_repo.is_enable_public_sale_house(house_id=dto.house_id):
            return UseCaseFailureOutput(
                type="house_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )
        # 사용자가 해당 house에 찜하기 되어있는지 여부
        is_like = self._house_repo.is_user_liked_house(
            self._house_repo.get_public_interest_house(dto=dto)
        )

        # 분양 매물 상세 query -> house_with_public_sales
        (
            house_with_public_sales,
            housing_category,
        ) = self._house_repo.get_house_with_public_sales(house_id=dto.house_id)
        if not house_with_public_sales:
            return UseCaseFailureOutput(
                type="house_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # get button link list
        # 민영 url
        if self._is_private_category(housing_category=housing_category):
            button_link_list = self._get_button_link_list(
                section_type=ButtonSectionType.PUBLIC_SALE_DETAIL_PRIVATE_REGISTRATION.value
            )
        # 공공 url
        else:
            button_link_list = self._get_button_link_list(
                section_type=ButtonSectionType.PUBLIC_SALE_DETAIL_PUBLIC_REGISTRATION.value
            )

        # get house ticket usage results
        ticket_usage_results = None
        if self.__is_ticket_usage_for_house(user_id=dto.user_id, house_id=dto.house_id):
            ticket_usage_results = self.__get_ticket_usage_results(
                user_id=dto.user_id, type_=TicketUsageTypeEnum.HOUSE.value
            )

        if ticket_usage_results:
            index = None
            # filter house_id, is_active
            for idx, ticket_usage_result in enumerate(ticket_usage_results):
                if (
                    ticket_usage_result.public_house_id == dto.house_id
                    and ticket_usage_result.is_active is True
                ):
                    index = idx
                    break

            if index >= 0:
                HouseHelper().sort_predicted_competition(
                    house_type_ranks=ticket_usage_results[index].house_type_ranks
                )
                ticket_usage_results = TicketUsageResultForHousePublicDetailEntity(
                    house_type_ranks=ticket_usage_results[index].house_type_ranks
                )

        # real_estates, public_sales, details, photos, button, ticket
        entities: HousePublicDetailEntity = self._house_repo.make_house_public_detail_entity(
            house_with_public_sales=house_with_public_sales,
            is_like=is_like,
            button_link_list=button_link_list,
            ticket_usage_results=ticket_usage_results,
        )

        house_applicants_dict: Dict = ReportHelper().make_response_object_to_house_applicants(
            report_recently_public_sale_info=entities.report_recently_public_sale_info
        )

        public_sale_detail_dict: Dict = ReportHelper().make_response_object_to_public_sale_details(
            report_recently_public_sale_info=entities.report_recently_public_sale_info
        )

        response_schema: HousePublicDetailSchema = self._make_response_schema(
            house_public_detail_entity=entities,
            house_applicants_dict=house_applicants_dict,
            public_sale_detail_dict=public_sale_detail_dict,
        )

        recently_view_dto = RecentlyViewDto(
            user_id=dto.user_id,
            house_id=dto.house_id,
            type=HouseTypeEnum.PUBLIC_SALES.value,
        )

        # User domain -> 최근 목록 리스트 생성 pypubsub 요청
        self.__create_recently_view(dto=recently_view_dto)

        return UseCaseSuccessOutput(value=response_schema)

    def __create_recently_view(self, dto: RecentlyViewDto) -> None:
        send_message(topic_name=UserTopicEnum.CREATE_RECENTLY_VIEW, dto=dto)
        return get_event_object(topic_name=UserTopicEnum.CREATE_RECENTLY_VIEW)

    def __is_ticket_usage_for_house(self, user_id: int, house_id: int) -> bool:
        send_message(
            topic_name=ReportTopicEnum.IS_TICKET_USAGE_FOR_HOUSE,
            user_id=user_id,
            house_id=house_id,
        )
        return get_event_object(topic_name=ReportTopicEnum.IS_TICKET_USAGE_FOR_HOUSE)

    def __get_ticket_usage_results(
        self, user_id: int, type_: str
    ) -> List[TicketUsageResultEntity]:
        send_message(
            topic_name=ReportTopicEnum.GET_TICKET_USAGE_RESULTS,
            user_id=user_id,
            type_=type_,
        )
        return get_event_object(topic_name=ReportTopicEnum.GET_TICKET_USAGE_RESULTS)


class GetHousePublicNearPrivateSalesUseCase(HouseBaseUseCase):
    def execute(
        self, dto: GetHousePublicNearPrivateSalesDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not self._house_repo.is_enable_public_sale_house(house_id=dto.house_id):
            return UseCaseFailureOutput(
                type="house_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        coordinates = self._house_repo.get_geometry_coordinates_from_public_sale(
            dto.house_id
        )

        if not coordinates:
            return UseCaseFailureOutput(
                type="coordinates",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # degree 테스트 필요: app에 나오는 반경 범위를 보면서 degree 조절 필요합니다.
        bounding_filter = self._house_repo.get_bounding_filter_with_radius(
            geometry_coordinates=coordinates, degree=BoundingDegreeEnum.DEGREE.value
        )

        bounding_entities = self._house_repo.get_near_houses_bounding(
            bounding_filter=bounding_filter
        )

        return UseCaseSuccessOutput(value=bounding_entities)


class GetCalendarInfoUseCase(HouseBaseUseCase):
    def execute(
        self, dto: GetCalendarInfoDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        year_month = dto.year + dto.month
        search_filters = self._house_repo.get_calendar_info_filters(
            year_month=year_month
        )
        calendar_entities = self._house_repo.get_simple_calendar_info(
            user_id=dto.user_id, search_filters=search_filters
        )

        return UseCaseSuccessOutput(value=calendar_entities)


class GetInterestHouseListUseCase(HouseBaseUseCase):
    def execute(
        self, dto: GetUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        result: List[
            InterestHouseListEntity
        ] = self._house_repo.get_interest_house_list(dto=dto)

        return UseCaseSuccessOutput(value=result)


class GetRecentViewListUseCase(HouseBaseUseCase):
    def execute(
        self, dto: GetUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        result: List[GetRecentViewListEntity] = self._house_repo.get_recent_view_list(
            dto=dto
        )

        return UseCaseSuccessOutput(value=result)


class UpdateRecentViewListUseCase(HouseBaseUseCase):
    def execute(
        self, dto: UpdateRecentViewListDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        self._house_repo.update_recent_view_list(dto=dto)

        return UseCaseSuccessOutput()


class GetSearchHouseListUseCase(HouseBaseUseCase):
    def execute(
        self, dto: GetSearchHouseListDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.keywords or dto.keywords == "" or len(dto.keywords) < 2:
            return UseCaseSuccessOutput(value=[])

        result: List[MapSearchEntity] = self._house_repo.get_search_house_list(
            keywords=dto.keywords
        )

        return UseCaseSuccessOutput(value=result)


class BoundingWithinRadiusUseCase(HouseBaseUseCase):
    def execute(
        self, dto: BoundingWithinRadiusDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:

        if (
            not dto
            or dto.search_type < SearchTypeEnum.FROM_REAL_ESTATE.value
            or dto.search_type > SearchTypeEnum.FROM_ADMINISTRATIVE_DIVISION.value
        ):
            return UseCaseFailureOutput(
                type="BoundingWithinRadiusDto",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )
        coordinates = None
        private_filter = list()
        public_filter = list()

        if dto.search_type == SearchTypeEnum.FROM_REAL_ESTATE.value:
            coordinates = self._house_repo.get_geometry_coordinates_from_real_estate(
                dto.house_id
            )
            private_filter = self._house_repo.get_bounding_private_type_filter(
                private_type=BoundingPrivateTypeEnum.APT_ONLY.value
            )
        elif dto.search_type == SearchTypeEnum.FROM_PUBLIC_SALE.value:
            coordinates = self._house_repo.get_geometry_coordinates_from_public_sale(
                dto.house_id
            )
            public_filter = self._house_repo.get_bounding_public_type_filter(
                public_type=BoundingPublicTypeEnum.ALL_PRE_SALE.value
            )
        elif dto.search_type == SearchTypeEnum.FROM_ADMINISTRATIVE_DIVISION.value:
            coordinates = self._house_repo.get_geometry_coordinates_from_administrative_division(
                dto.house_id
            )
            private_filter = self._house_repo.get_bounding_private_type_filter(
                private_type=BoundingPrivateTypeEnum.APT_ONLY.value
            )

        if not coordinates:
            return UseCaseFailureOutput(
                type="coordinates",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # degree 테스트 필요: app에 나오는 반경 범위를 보면서 degree 조절 필요합니다.
        bounding_filter = self._house_repo.get_bounding_filter_with_radius(
            geometry_coordinates=coordinates, degree=BoundingDegreeEnum.DEGREE.value
        )
        bounding_entities = self._house_repo.get_bounding(
            bounding_filter=bounding_filter,
            private_filters=private_filter,
            public_filters=public_filter,
            min_area=None,
            max_area=None,
        )

        return UseCaseSuccessOutput(value=bounding_entities)


class GetHouseMainUseCase(HouseBaseUseCase):
    def _make_house_main_entity(
        self,
        banner_list: List[BannerEntity],
        calendar_entities: List[SimpleCalendarInfoEntity],
        recent_public_info_entities: List[MainRecentPublicInfoEntity],
    ) -> GetHouseMainEntity:
        return GetHouseMainEntity(
            banner_list=banner_list,
            calendar_infos=calendar_entities,
            recent_public_infos=recent_public_info_entities,
        )

    def _make_recent_public_info_entity(
        self, recent_public_infos: list
    ) -> List[MainRecentPublicInfoEntity]:
        entity_list = list()
        for query in recent_public_infos:
            entity_list.append(
                MainRecentPublicInfoEntity(
                    id=query.id,
                    name=query.name,
                    status=HouseHelper().public_status(
                        offer_date=query.offer_date,
                        subscription_end_date=query.subscription_end_date,
                    ),
                    si_do=query.si_do,
                    public_sale_photo=S3Helper().get_cloudfront_url()
                    + "/"
                    + query.public_sale_photo
                    if query.public_sale_photo
                    else None,
                )
            )

        return entity_list

    def _sort_recent_public_infos_about_capital_area(
        self, recent_public_info_entities: List[MainRecentPublicInfoEntity]
    ):
        """
            최근 분양정보 수도권 우선 소팅(서울, 경기, 인천)
        """
        capital_area = tuple([elm.value for elm in list(CapitalAreaEnum)])
        length = len(recent_public_info_entities)

        if not length:
            return None

        for i in range(length - 1):
            for j in range(i + 1, length):
                if (
                    recent_public_info_entities[j].si_do in capital_area
                    and recent_public_info_entities[i].si_do not in capital_area
                ):
                    recent_public_info_entities[i], recent_public_info_entities[j] = (
                        recent_public_info_entities[j],
                        recent_public_info_entities[i],
                    )

    def execute(
        self, dto: GetHouseMainDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if dto.section_type != SectionType.HOME_SCREEN.value:
            return UseCaseFailureOutput(
                type="section_type",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )
        # get house main banner list
        banner_list = self._get_banner_list(section_type=dto.section_type)

        # 이미지가 없을 경우 이미지 없이 나오도록 쿼리
        # 이 경우, 기본 이미지는 FE 쪽에서 처리
        recent_public_infos = self._house_repo.get_main_recent_public_info_list()

        if not recent_public_infos:
            return UseCaseFailureOutput(
                type="recent_public_infos",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        recent_public_info_entities = self._make_recent_public_info_entity(
            recent_public_infos=recent_public_infos
        )

        # 수도권 우선 정렬
        self._sort_recent_public_infos_about_capital_area(
            recent_public_info_entities=recent_public_info_entities
        )

        # get present calendar info
        now = get_server_timestamp()
        year = str(now.year)
        month = str(now.month)

        if 0 < now.month < 10:
            month = "0" + month

        year_month = year + month

        search_filters = self._house_repo.get_calendar_info_filters(
            year_month=year_month
        )
        calendar_entities = self._house_repo.get_simple_calendar_info(
            user_id=dto.user_id, search_filters=search_filters
        )

        result = self._make_house_main_entity(
            banner_list=banner_list,
            calendar_entities=calendar_entities,
            recent_public_info_entities=recent_public_info_entities,
        )
        return UseCaseSuccessOutput(value=result)


class GetMainPreSubscriptionUseCase(HouseBaseUseCase):
    def _make_house_main_pre_subscription_entity(
        self, banner_list: List[BannerEntity], button_links: List[ButtonLinkEntity]
    ) -> GetMainPreSubscriptionEntity:
        return GetMainPreSubscriptionEntity(
            banner_list=banner_list, button_links=button_links
        )

    def execute(
        self, dto: SectionTypeDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if dto.section_type != SectionType.PRE_SUBSCRIPTION_INFO.value:
            return UseCaseFailureOutput(
                type="section_type",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )
        # get home banner list
        banner_list = self._get_banner_list(section_type=dto.section_type)
        # get button link list
        button_link_list = self._get_button_link_list(section_type=dto.section_type)

        result = self._make_house_main_pre_subscription_entity(
            banner_list=banner_list, button_links=button_link_list
        )
        return UseCaseSuccessOutput(value=result)
