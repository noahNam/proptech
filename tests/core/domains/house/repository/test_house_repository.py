from app import InterestHouseModel
from core.domains.house.dto.house_dto import InterestHouseDto
from core.domains.house.enum.house_enum import HouseTypeEnum
from core.domains.house.repository.house_repository import HouseRepository

interest_house_dto = InterestHouseDto(
    user_id=1,
    ref_id=1,
    type=HouseTypeEnum.PUBLIC_SALES.value,
    is_like=True
)


def test_create_like_house_repo_when_user_select_public_sales_then_success(session):
    HouseRepository().create_interest_house(dto=interest_house_dto)

    filters = list()
    filters.append(InterestHouseModel.user_id == interest_house_dto.user_id)
    filters.append(InterestHouseModel.ref_id == interest_house_dto.ref_id)
    filters.append(InterestHouseModel.type == interest_house_dto.type)

    result = session.query(InterestHouseModel).filter(*filters).first()

    assert result.is_like == interest_house_dto.is_like
    assert result.user_id == interest_house_dto.user_id
    assert result.ref_id == interest_house_dto.ref_id
    assert result.type == interest_house_dto.type


def test_update_is_like_house_repo_when_user_select_public_sales_then_success(session, interest_house_factory):
    interest_house = interest_house_factory.build()
    session.add(interest_house)
    session.commit()

    interest_house_dto.is_like = False
    HouseRepository().update_interest_house(dto=interest_house_dto)

    filters = list()
    filters.append(InterestHouseModel.user_id == interest_house_dto.user_id)
    filters.append(InterestHouseModel.ref_id == interest_house_dto.ref_id)
    filters.append(InterestHouseModel.type == interest_house_dto.type)

    result = session.query(InterestHouseModel).filter(*filters).first()

    assert result.is_like == interest_house_dto.is_like
    assert result.user_id == interest_house_dto.user_id
    assert result.ref_id == interest_house_dto.ref_id
    assert result.type == interest_house_dto.type
