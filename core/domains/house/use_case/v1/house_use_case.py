# from http import HTTPStatus
# from typing import Union
#
# import inject
#
# from core.domains.house.dto.house_dto import CoordinatesRangeDto
# from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType
#
#
# class MapBoundingUseCase:
#     @inject.autoparams()
#     def __init__(self, map_repo: HouseRepository):
#         self._map_repo = map_repo
#
#     def execute(
#             self, dto: CoordinatesRangeDto
#     ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
#         if not (dto.start_x and dto.start_y and dto.end_x and dto.end_y):
#             return UseCaseFailureOutput(
#                 type="map_coordinates", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
#             )
#         bounding_result = self._map_repo.get_estates_by_coordinates_range_dto(dto=dto)
#
#         UseCaseSuccessOutput(value=bounding_result)