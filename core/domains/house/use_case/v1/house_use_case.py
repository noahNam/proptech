from http import HTTPStatus
from typing import Union

import inject

from core.domains.house.dto.house_dto import CoordinatesRangeDto
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.repository.house_repository import HouseRepository
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
                type="map_coordinates", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )
        # dto.level range check
        if dto.level < 5 or dto.level > 22:
            return UseCaseFailureOutput(
                type="level", message=FailureType.INVALID_REQUEST_ERROR, code=HTTPStatus.BAD_REQUEST
            )
        # dto.level condition
        if dto.level > 14:
            bounding_entities = self._house_repo.get_queryset_by_coordinates_range_dto(dto=dto)
        else:
            bounding_entities = self._house_repo.get_administrative_queryset_by_coordinates_range_dto(dto=dto)

        if not bounding_entities:
            return UseCaseSuccessOutput(value="null")
        return UseCaseSuccessOutput(value=bounding_entities)
