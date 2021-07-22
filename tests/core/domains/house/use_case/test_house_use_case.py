from unittest.mock import patch

from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import UpsertInterestHouseDto, CoordinatesRangeDto
from core.domains.house.enum.house_enum import HouseTypeEnum, BoundingLevelEnum
from core.domains.house.use_case.v1.house_use_case import UpsertInterestHouseUseCase, BoundingUseCase
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType

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
    level=BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value
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


def test_bounding_use_case_when_get_wrong_level_then_400_error(session, create_real_estate_with_bounding):
    """
        level 값이 범위 밖이면 400 에러
    """
    wrong_dto = CoordinatesRangeDto(
        start_x=126.5,
        start_y=37.7,
        end_x=127.9,
        end_y=37.42,
        level=23
    )
    result = BoundingUseCase().execute(dto=wrong_dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.code == 400
    assert result.type == "level"
    assert result.message == FailureType.INVALID_REQUEST_ERROR


def test_bounding_use_case_when_get_no_coordinates_then_404_error(session, create_real_estate_with_bounding):
    """
        좌표 값이 없으면(0이면) 404 에러
    """
    wrong_dto = CoordinatesRangeDto(
        start_x=0,
        start_y=37.7,
        end_x=127.9,
        end_y=37.42,
        level=15
    )
    result = BoundingUseCase().execute(dto=wrong_dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.code == 404
    assert result.type == "map_coordinates"
    assert result.message == FailureType.NOT_FOUND_ERROR


def test_bounding_use_case_when_level_is_grater_than_queryset_flag_then_call_get_bounding(
        session, create_real_estate_with_bounding):
    """
        level 값이 BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value 이상이면
        HouseRepository().get_bounding_by_coordinates_range_dto 호출
    """
    with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_bounding_by_coordinates_range_dto"
    ) as mock_get_bounding:
        mock_get_bounding.return_value = create_real_estate_with_bounding
        result = BoundingUseCase().execute(dto=coordinates_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_get_bounding.called is True
    assert result.value == mock_get_bounding.return_value


def test_bounding_use_case_when_level_is_lower_than_queryset_flag_then_call_get_administrative(
        session, create_real_estate_with_bounding):
    """
        level 값이 BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value 미만이면
        HouseRepository().get_administrative_by_coordinates_range_dto 호출
    """
    lower_dto = CoordinatesRangeDto(
        start_x=126.5,
        start_y=37.7,
        end_x=127.9,
        end_y=37.42,
        level=BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value - 1
    )
    with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_administrative_by_coordinates_range_dto"
    ) as mock_get_bounding:
        mock_get_bounding.return_value = create_real_estate_with_bounding
        result = BoundingUseCase().execute(dto=lower_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_get_bounding.called is True
    assert result.value == mock_get_bounding.return_value
