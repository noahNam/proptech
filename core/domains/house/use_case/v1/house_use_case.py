from http import HTTPStatus
from typing import Union

import inject

from core.domains.house.dto.house_dto import InterestHouseDto
from core.domains.house.repository.house_repository import HouseRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class HouseBaseUseCase:
    @inject.autoparams()
    def __init__(self, house_repo: HouseRepository):
        self._house_repo = house_repo


class CreateInterestHouseUseCase(HouseBaseUseCase):
    def execute(self, dto: InterestHouseDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )

        self._house_repo.create_interest_house(dto=dto)
        return UseCaseSuccessOutput()


class UpdateInterestHouseUseCase(HouseBaseUseCase):
    def execute(self, dto: InterestHouseDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )

        self._house_repo.update_interest_house(dto=dto)
        return UseCaseSuccessOutput()
