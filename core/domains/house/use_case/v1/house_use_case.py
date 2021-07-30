from http import HTTPStatus
from typing import Union, List, Optional

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
from core.domains.house.dto.house_dto import (
    CoordinatesRangeDto,
    GetHousePublicDetailDto,
    GetCalenderInfoDto,
    GetSearchHouseListDto,
    BoundingWithinRadiusDto,
)
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.entity.house_entity import (
    InterestHouseListEntity,
    GetRecentViewListEntity,
    BoundingRealEstateEntity,
    GetSearchHouseListEntity,
    GetRecentViewListEntity,
    PublicSaleEntity,
    GetTicketUsageResultEntity,
)
from core.domains.house.enum.house_enum import (
    BoundingLevelEnum,
    HouseTypeEnum,
    SearchTypeEnum,
)
from core.domains.house.repository.house_repository import HouseRepository
from core.domains.user.dto.user_dto import RecentlyViewDto, GetUserDto
from core.domains.user.enum import UserTopicEnum
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class HouseBaseUseCase:
    @inject.autoparams()
    def __init__(self, house_repo: HouseRepository):
        self._house_repo = house_repo


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

        interest_house: InterestHouseModel = self._house_repo.update_interest_house(
            dto=dto
        )
        if not interest_house:
            self._house_repo.create_interest_house(dto=dto)

        return UseCaseSuccessOutput()


class BoundingUseCase(HouseBaseUseCase):
    def execute(
        self, dto: CoordinatesRangeDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        """
            <dto.level condition>
                level 15 이상 : 매물 쿼리
                level 14 이하 : 행정구역별 평균 가격 쿼리
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
        if not self._house_repo.is_enable_public_sale_house(dto=dto):
            return UseCaseFailureOutput(
                type="house_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )
        # 사용자가 해당 house에 찜하기 되어있는지 여부
        is_like = self._house_repo.is_user_liked_house(
            self._house_repo.get_public_interest_house(dto=dto)
        )

        # get HousePublicDetailEntity (degree 조절 필요)
        entities = self._house_repo.get_house_public_detail(
            dto=dto, degree=1, is_like=is_like
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


class GetCalenderInfoUseCase(HouseBaseUseCase):
    def execute(
        self, dto: GetCalenderInfoDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        calender_entities = self._house_repo.get_calender_info(dto=dto)

        return UseCaseSuccessOutput(value=calender_entities)


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


class GetTicketUsageResultUseCase(HouseBaseUseCase):
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
            GetTicketUsageResultEntity
        ] = self._house_repo.get_ticket_usage_results(dto=dto)

        return UseCaseSuccessOutput(value=result)


class GetSearchHouseListUseCase(HouseBaseUseCase):
    def execute(
        self, dto: GetSearchHouseListDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.keywords or dto.keywords == "" or len(dto.keywords) < 2:
            result = None
            return UseCaseSuccessOutput(value=result)

        result: Optional[
            GetSearchHouseListEntity
        ] = self._house_repo.get_search_house_list(dto=dto)

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
            geometry_coordinates=coordinates, degree=1
        )
        bounding_entities = self._house_repo.get_bounding(
            bounding_filter=bounding_filter
        )

        return UseCaseSuccessOutput(value=bounding_entities)
