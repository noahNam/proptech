from http import HTTPStatus
from typing import Union, List, Optional

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
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
)
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.entity.house_entity import (
    GetSearchHouseListEntity,
    GetRecentViewListEntity,
    GetMainPreSubscriptionEntity,
    GetHouseMainEntity,
    SimpleCalendarInfoEntity,
    InterestHouseListEntity,
    HousePublicDetailEntity, MapSearchEntity,
)
from core.domains.house.enum.house_enum import (
    BoundingLevelEnum,
    HouseTypeEnum,
    SearchTypeEnum,
    SectionType,
    BoundingDegreeEnum,
)
from core.domains.house.repository.house_repository import HouseRepository
from core.domains.report.entity.report_entity import TicketUsageResultEntity
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
        # dto.level condition
        if dto.level >= BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value:
            bounding_filter = self._house_repo.get_bounding_filter_with_two_points(
                dto=dto
            )
            bounding_entities = self._house_repo.get_bounding(
                bounding_filter=bounding_filter
            )
        else:
            bounding_entities = self._house_repo.get_administrative_divisions(dto=dto)

        return UseCaseSuccessOutput(value=bounding_entities)


class GetHousePublicDetailUseCase(HouseBaseUseCase):
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
        house_with_public_sales = self._house_repo.get_house_with_public_sales(
            house_id=dto.house_id
        )
        if not house_with_public_sales:
            return UseCaseFailureOutput(
                type="house_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # get button link list
        button_link_list = self._get_button_link_list(
            section_type=SectionType.PUBLIC_SALE_DETAIL.value
        )

        # get house ticket usage results
        ticket_usage_results = None
        if self.__is_ticket_usage_for_house(user_id=dto.user_id, house_id=dto.house_id):
            ticket_usage_results = self.__get_ticket_usage_results(
                user_id=dto.user_id, type_=TicketUsageTypeEnum.HOUSE.value
            )

        entities: HousePublicDetailEntity = self._house_repo.make_house_public_detail_entity(
            house_with_public_sales=house_with_public_sales,
            is_like=is_like,
            button_link_list=button_link_list,
            ticket_usage_results=ticket_usage_results,
        )

        recently_view_dto = RecentlyViewDto(
            user_id=dto.user_id,
            house_id=dto.house_id,
            type=HouseTypeEnum.PUBLIC_SALES.value,
        )

        # User domain -> 최근 목록 리스트 생성 pypubsub 요청
        self.__create_recently_view(dto=recently_view_dto)

        return UseCaseSuccessOutput(value=entities)

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

            # 분양 매물 상세 query -> house_with_public_sales
        house_with_public_sales = self._house_repo.get_house_with_public_sales(
            house_id=dto.house_id
        )

        entities = self._house_repo.get_public_with_private_sales_in_radius(
            house_with_public_sales=house_with_public_sales,
            degree=BoundingDegreeEnum.DEGREE.value,
        )

        return UseCaseSuccessOutput(value=entities)


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


class GetSearchHouseListUseCase(HouseBaseUseCase):
    def execute(
        self, dto: GetSearchHouseListDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.keywords or dto.keywords == "" or len(dto.keywords) < 2:
            return UseCaseSuccessOutput()

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
        if dto.search_type == SearchTypeEnum.FROM_REAL_ESTATE.value:
            coordinates = self._house_repo.get_geometry_coordinates_from_real_estate(
                dto.house_id
            )
        elif dto.search_type == SearchTypeEnum.FROM_PUBLIC_SALE.value:
            coordinates = self._house_repo.get_geometry_coordinates_from_public_sale(
                dto.house_id
            )
        elif dto.search_type == SearchTypeEnum.FROM_ADMINISTRATIVE_DIVISION.value:
            coordinates = self._house_repo.get_geometry_coordinates_from_administrative_division(
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
        bounding_entities = self._house_repo.get_bounding(
            bounding_filter=bounding_filter
        )

        return UseCaseSuccessOutput(value=bounding_entities)


class GetHouseMainUseCase(HouseBaseUseCase):
    def _make_house_main_entity(
        self,
        banner_list: List[BannerEntity],
        calendar_entities: List[SimpleCalendarInfoEntity],
    ) -> GetHouseMainEntity:
        return GetHouseMainEntity(
            banner_list=banner_list, calendar_infos=calendar_entities
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
            banner_list=banner_list, calendar_entities=calendar_entities
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
