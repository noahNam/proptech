from http import HTTPStatus
from typing import Union

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
from core.domains.house.dto.house_dto import CoordinatesRangeDto, GetHousePublicDetailDto, GetCalenderInfoDto
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.enum.house_enum import BoundingLevelEnum
from core.domains.house.repository.house_repository import HouseRepository
from core.domains.user.dto.user_dto import RecentlyViewDto
from core.domains.user.enum import UserTopicEnum
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class HouseBaseUseCase:
    @inject.autoparams()
    def __init__(self, house_repo: HouseRepository):
        self._house_repo = house_repo


class UpsertInterestHouseUseCase(HouseBaseUseCase):
    def execute(self, dto: UpsertInterestHouseDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )

        interest_house: InterestHouseModel = self._house_repo.update_interest_house(dto=dto)
        if not interest_house:
            self._house_repo.create_interest_house(dto=dto)

        return UseCaseSuccessOutput()


class BoundingUseCase(HouseBaseUseCase):
    def execute(self, dto: CoordinatesRangeDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        """
            <dto.level condition>
                level 15 이상 : 매물 쿼리
                level 14 이하 : 행정구역별 평균 가격 쿼리
                level 값 조절시 bounding_view()의 presenter 선택 조건 고려해야 합니다.
        """
        if not (dto.start_x and dto.start_y and dto.end_x and dto.end_y and dto.level):
            return UseCaseFailureOutput(
                type="map_coordinates", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )
        # dto.level range check
        if dto.level < BoundingLevelEnum.MIN_NAVER_MAP_API_ZOOM_LEVEL.value \
                or dto.level > BoundingLevelEnum.MAX_NAVER_MAP_API_ZOOM_LEVEL.value:
            return UseCaseFailureOutput(
                type="level", message=FailureType.INVALID_REQUEST_ERROR, code=HTTPStatus.BAD_REQUEST
            )
        # dto.level condition
        if dto.level >= BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value:
            bounding_entities = self._house_repo.get_bounding_by_coordinates_range_dto(dto=dto)
        else:
            bounding_entities = self._house_repo.get_administrative_by_coordinates_range_dto(dto=dto)

        if not bounding_entities:
            return UseCaseSuccessOutput(value="null")
        return UseCaseSuccessOutput(value=bounding_entities)


class GetHousePublicDetailUseCase(HouseBaseUseCase):
    def execute(self, dto: GetHousePublicDetailDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not self._house_repo.is_enable_public_sale_house(dto=dto):
            return UseCaseFailureOutput(
                type="house_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )
        # 사용자가 해당 house에 찜하기 되어있는지 여부
        is_like = self._house_repo.is_user_liked_house(self._house_repo.get_public_interest_house(dto=dto))

        # get HousePublicDetailEntity (degrees 조절 필요)
        entities = self._house_repo \
            .get_house_public_detail_by_get_house_public_detail_dto(dto=dto, degrees=1, is_like=is_like)

        recently_view_dto = RecentlyViewDto(user_id=dto.user_id, house_id=dto.house_id, type=1)

        # User domain -> 최근 목록 리스트 생성 pypubsub 요청
        self.__create_recently_view(dto=recently_view_dto)

        return UseCaseSuccessOutput(value=entities)

    def __create_recently_view(self, dto: RecentlyViewDto) -> None:
        send_message(topic_name=UserTopicEnum.CREATE_RECENTLY_VIEW, dto=dto)
        return get_event_object(topic_name=UserTopicEnum.CREATE_RECENTLY_VIEW)


class GetCalenderInfoUseCase(HouseBaseUseCase):
    def execute(self, dto: GetCalenderInfoDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        calender_entities = self._house_repo.get_calender_info_by_get_calender_info_dto(dto=dto)
        if not calender_entities:
            return UseCaseSuccessOutput(value="null")
        return UseCaseSuccessOutput(value=calender_entities)
