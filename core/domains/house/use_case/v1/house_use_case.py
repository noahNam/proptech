from http import HTTPStatus
from typing import Union

import inject

from core.domains.house.dto.house_dto import CoordinatesRangeDto
from core.domains.house.repository.house_repository import HouseRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class BoundingUseCase:
    @inject.autoparams()
    def __init__(self, map_repo: HouseRepository):
        self._map_repo = map_repo

    def execute(
            self, dto: CoordinatesRangeDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not (dto.start_x and dto.start_y and dto.end_x and dto.end_y):
            return UseCaseFailureOutput(
                type="map_coordinates", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )
        # queryset2 = self._map_repo.get_queryset_by_coordinates_range_dto2(dto=dto)
        queryset = self._map_repo.get_queryset_by_coordinates_range_dto(dto=dto)
        self._make_object_bounding_entity_from_queryset(queryset=queryset)

        UseCaseSuccessOutput(value=None)

    def _make_object_bounding_entity_from_queryset(self, queryset: list):
        if not queryset:
            return None

        # Make Entity
        results = list()
        try:
            for query in queryset:
                results.append(query.to_bounding_entity())
                # 검증용으로 dict 변환
                # results.append(query.to_bounding_entity().dict())
        except Exception as e:
            pass

        print("*" * 30)
        print(results)
        print("*" * 30)
