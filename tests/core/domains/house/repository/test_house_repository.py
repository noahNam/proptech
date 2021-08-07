from unittest.mock import patch

from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import (
    UpsertInterestHouseDto,
    CoordinatesRangeDto,
    GetHousePublicDetailDto,
    GetCalendarInfoDto,
    GetSearchHouseListDto,
)
from core.domains.house.entity.house_entity import (
    SearchRealEstateEntity,
    SearchPublicSaleEntity,
    SearchAdministrativeDivisionEntity,
    GetSearchHouseListEntity,
)
from core.domains.house.enum.house_enum import HouseTypeEnum
from core.domains.house.repository.house_repository import HouseRepository
from core.domains.user.dto.user_dto import GetUserDto

upsert_interest_house_dto = UpsertInterestHouseDto(
    user_id=1, house_id=1, type=HouseTypeEnum.PUBLIC_SALES.value, is_like=True
)

coordinates_dto = CoordinatesRangeDto(
    start_x=126.5, start_y=37.7, end_x=127.9, end_y=37.42, level=15
)

get_house_public_detail_dto = GetHousePublicDetailDto(user_id=1, house_id=1)

get_calendar_info_dto = GetCalendarInfoDto(year=2021, month=7, user_id=1)


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


def test_update_is_like_house_repo_when_unlike_public_sales_then_success(
    session, interest_house_factory
):
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


def test_get_bounding_by_coordinates_range_dto(
    session, create_real_estate_with_bounding
):
    """
        get_bounding_by_coordinates_range_dto -> return mocking
    """
    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_bounding"
    ) as mock_get_bounding:
        mock_get_bounding.return_value = create_real_estate_with_bounding
        result = HouseRepository().get_bounding(dto=coordinates_dto)

    assert result == mock_get_bounding.return_value
    assert mock_get_bounding.called is True


def test_get_administrative_by_coordinates_range_dto(
    session, create_real_estate_with_bounding
):
    """
        get_administrative_by_coordinates_range_dto -> return mocking
    """
    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_administrative_divisions"
    ) as mock_get_bounding:
        mock_get_bounding.return_value = create_real_estate_with_bounding
        result = HouseRepository().get_administrative_divisions(dto=coordinates_dto)

    assert result == mock_get_bounding.return_value
    assert mock_get_bounding.called is True


def test_get_public_interest_house(session, create_interest_house):
    dto = get_house_public_detail_dto
    result = HouseRepository().get_public_interest_house(dto=dto)

    assert result.user_id == dto.user_id
    assert result.house_id == dto.house_id
    assert result.type == HouseTypeEnum.PUBLIC_SALES.value
    assert result.is_like is True


def test_is_user_liked_house(session, create_interest_house):
    result = HouseRepository().is_user_liked_house(create_interest_house[0])
    assert result is True


def test_get_house_public_detail_when_get_house_public_detail_dto(
    session, create_real_estate_with_public_sale
):
    """
        get_house_public_detail_by_get_house_public_detail_dto -> return mocking
    """
    dto = get_house_public_detail_dto
    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_house_public_detail"
    ) as mock_house_public_detail:
        mock_house_public_detail.return_value = create_real_estate_with_public_sale[0]
        result = HouseRepository().get_house_public_detail(
            dto=dto, degree=1, is_like=True
        )
    assert result == mock_house_public_detail.return_value
    assert mock_house_public_detail.called is True


def test_get_calendar_info_when_get_calendar_info_dto(
    session, create_real_estate_with_public_sale
):
    """
        get_calendar_info_by_get_calendar_info_dto -> return mocking
    """
    dto = get_calendar_info_dto
    year_month = get_calendar_info_dto.year + get_calendar_info_dto.month
    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = create_real_estate_with_public_sale[0]
        search_filters = HouseRepository().get_calendar_info_filters(
            year_month=year_month
        )
        result = HouseRepository().get_calendar_info(
            user_id=dto.user_id, search_filters=search_filters
        )

    assert result == mock_calendar_info.return_value
    assert mock_calendar_info.called is True


def test_get_interest_house_list_then_entity_result(
    session, create_users, create_real_estate_with_public_sale
):
    dto = GetUserDto(user_id=create_users[0].id)
    result = HouseRepository().get_interest_house_list(dto=dto)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].house_id == 1
    assert result[0].road_address is not None


def test_get_recent_view_list_then_entity_result(
    session,
    create_users,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
):
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)
    session.add(public_sale_photo)
    session.commit()

    dto = GetUserDto(user_id=create_users[0].id)
    result = HouseRepository().get_recent_view_list(dto=dto)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].image_path == public_sale_photo_factory.path


def test_get_search_house_list_when_get_keywords(
    session, create_real_estate_with_public_sale
):
    dto = GetSearchHouseListDto(keywords="서울")
    real_estates = [
        SearchRealEstateEntity(
            id=1, jibun_address="서울시 서초구 어딘가", road_address="서울시 서초구 어딘가길"
        )
    ]
    public_sales = [SearchPublicSaleEntity(id=2, name="서울숲아파트")]
    administrative_divisions = [
        SearchAdministrativeDivisionEntity(id=3, name="서울특별시 서초구")
    ]

    mock_result = GetSearchHouseListEntity(
        real_estates=real_estates,
        public_sales=public_sales,
        administrative_divisions=administrative_divisions,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_search_house_list"
    ) as mock_search:
        mock_search.return_value = mock_result
        result = HouseRepository().get_search_house_list(dto=dto)

    assert isinstance(result, GetSearchHouseListEntity)
