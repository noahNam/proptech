from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.domains.house.enum.house_enum import HouseTypeEnum
from core.domains.house.use_case.v1.house_use_case import UpsertInterestHouseUseCase
from core.use_case_output import UseCaseSuccessOutput

upsert_interest_house_dto = UpsertInterestHouseDto(
    user_id=1,
    house_id=1,
    type=HouseTypeEnum.PUBLIC_SALES.value,
    is_like=True
)


def test_upsert_interest_house_use_case_when_like_public_sales_then_success(session):
    result = UpsertInterestHouseUseCase().execute(dto=upsert_interest_house_dto)

    filters = list()
    filters.append(InterestHouseModel.user_id == upsert_interest_house_dto.user_id)
    filters.append(InterestHouseModel.house_id == upsert_interest_house_dto.house_id)
    filters.append(InterestHouseModel.type == upsert_interest_house_dto.type)

    interest_house = session.query(InterestHouseModel).filter(*filters).first()

    assert isinstance(result, UseCaseSuccessOutput)
    assert interest_house.is_like == upsert_interest_house_dto.is_like
    assert interest_house.user_id == upsert_interest_house_dto.user_id
    assert interest_house.house_id == upsert_interest_house_dto.house_id
    assert interest_house.type == upsert_interest_house_dto.type


def test_upsert_interest_house_use_case_when_unlike_public_sales_then_success(session,
                                                                              interest_house_factory):
    interest_house = interest_house_factory.build()
    session.add(interest_house)
    session.commit()

    upsert_interest_house_dto.is_like = False
    result = UpsertInterestHouseUseCase().execute(dto=upsert_interest_house_dto)

    filters = list()
    filters.append(InterestHouseModel.user_id == upsert_interest_house_dto.user_id)
    filters.append(InterestHouseModel.house_id == upsert_interest_house_dto.house_id)
    filters.append(InterestHouseModel.type == upsert_interest_house_dto.type)

    interest_house = session.query(InterestHouseModel).filter(*filters).first()

    assert isinstance(result, UseCaseSuccessOutput)
    assert interest_house.is_like is False
