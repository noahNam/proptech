from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto, CoordinatesRangeDto
from core.domains.house.enum.house_enum import HouseTypeEnum
from core.domains.house.repository.house_repository import HouseRepository

upsert_interest_house_dto = UpsertInterestHouseDto(
    user_id=1,
    house_id=1,
    type=HouseTypeEnum.PUBLIC_SALES.value,
    is_like=True
)

coordinates_dto = CoordinatesRangeDto(
    start_x=126.5,
    start_y=37.7,
    end_x=127.9,
    end_y=37.42,
    level=15
)


def test_create_like_house_repo_when_like_public_sales_then_success(session):
    HouseRepository().create_interest_house(dto=upsert_interest_house_dto)

    filters = list()
    filters.append(InterestHouseModel.user_id == upsert_interest_house_dto.user_id)
    filters.append(InterestHouseModel.house_id == upsert_interest_house_dto.house_id)
    filters.append(InterestHouseModel.type == upsert_interest_house_dto.type)

    result = session.query(InterestHouseModel).filter(*filters).first()

    assert result.is_like == upsert_interest_house_dto.is_like
    assert result.user_id == upsert_interest_house_dto.user_id
    assert result.house_id == upsert_interest_house_dto.house_id
    assert result.type == upsert_interest_house_dto.type


def test_update_is_like_house_repo_when_unlike_public_sales_then_success(session, interest_house_factory):
    interest_house = interest_house_factory.build()
    session.add(interest_house)
    session.commit()

    upsert_interest_house_dto.is_like = False
    HouseRepository().update_interest_house(dto=upsert_interest_house_dto)

    filters = list()
    filters.append(InterestHouseModel.user_id == upsert_interest_house_dto.user_id)
    filters.append(InterestHouseModel.house_id == upsert_interest_house_dto.house_id)
    filters.append(InterestHouseModel.type == upsert_interest_house_dto.type)

    result = session.query(InterestHouseModel).filter(*filters).first()

    assert result.is_like == upsert_interest_house_dto.is_like
    assert result.user_id == upsert_interest_house_dto.user_id
    assert result.house_id == upsert_interest_house_dto.house_id
    assert result.type == upsert_interest_house_dto.type


# def test_get_bounding_by_coordinates_range_dto(gis_session, real_estate_with_private_sale_factory):
#     result = HouseRepository().get_bounding_by_coordinates_range_dto(dto=coordinates_dto)
#     print(result)
