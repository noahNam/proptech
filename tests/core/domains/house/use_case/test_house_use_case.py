import pytest

from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import InterestHouseDto
from core.domains.house.enum.house_enum import HouseTypeEnum
from core.domains.house.use_case.v1.house_use_case import CreateInterestHouseUseCase, UpdateInterestHouseUseCase
from core.exceptions import NotUniqueErrorException
from core.use_case_output import UseCaseSuccessOutput

interest_house_dto = InterestHouseDto(
    user_id=1,
    ref_id=1,
    type=HouseTypeEnum.PUBLIC_SALES.value,
    is_like=True
)


def test_create_interest_house_use_case_when_like_public_sales_then_success(session):
    result = CreateInterestHouseUseCase().execute(dto=interest_house_dto)

    filters = list()
    filters.append(InterestHouseModel.user_id == interest_house_dto.user_id)
    filters.append(InterestHouseModel.ref_id == interest_house_dto.ref_id)
    filters.append(InterestHouseModel.type == interest_house_dto.type)

    interest_house = session.query(InterestHouseModel).filter(*filters).first()

    assert isinstance(result, UseCaseSuccessOutput)
    assert interest_house.is_like == interest_house_dto.is_like
    assert interest_house.user_id == interest_house_dto.user_id
    assert interest_house.ref_id == interest_house_dto.ref_id
    assert interest_house.type == interest_house_dto.type


def test_create_interest_house_use_case_when_like_public_sales_then_unique_error(session,
                                                                                 interest_house_factory):
    interest_house = interest_house_factory.build()
    session.add(interest_house)
    session.commit()

    with pytest.raises(NotUniqueErrorException):
        CreateInterestHouseUseCase().execute(dto=interest_house_dto)


def test_update_interest_house_use_case_when_unlike_public_sales_then_success(session,
                                                                              interest_house_factory):
    interest_house = interest_house_factory.build()
    session.add(interest_house)
    session.commit()

    interest_house_dto.is_like = False
    result = UpdateInterestHouseUseCase().execute(dto=interest_house_dto)

    filters = list()
    filters.append(InterestHouseModel.user_id == interest_house_dto.user_id)
    filters.append(InterestHouseModel.ref_id == interest_house_dto.ref_id)
    filters.append(InterestHouseModel.type == interest_house_dto.type)

    interest_house = session.query(InterestHouseModel).filter(*filters).first()

    assert isinstance(result, UseCaseSuccessOutput)
    assert interest_house.is_like is False
