from unittest.mock import patch

from app.persistence.model import InterestHouseModel, RecentlyViewModel
from core.domains.house.dto.house_dto import (
    UpsertInterestHouseDto,
    CoordinatesRangeDto,
    GetHousePublicDetailDto,
    GetCalenderInfoDto,
)
from core.domains.house.entity.house_entity import (
    PublicSaleCalenderEntity,
    CalenderInfoEntity,
)
from core.domains.house.enum.house_enum import HouseTypeEnum, BoundingLevelEnum
from core.domains.house.use_case.v1.house_use_case import (
    UpsertInterestHouseUseCase,
    BoundingUseCase,
    GetHousePublicDetailUseCase,
    GetCalenderInfoUseCase,
    GetInterestHouseListUseCase,
    GetRecentViewListUseCase,
)
from core.domains.user.dto.user_dto import GetUserDto
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType

upsert_interest_house_dto = UpsertInterestHouseDto(
    user_id=1, house_id=1, type=HouseTypeEnum.PUBLIC_SALES.value, is_like=True
)

coordinates_dto = CoordinatesRangeDto(
    start_x=126.5,
    start_y=37.7,
    end_x=127.9,
    end_y=37.42,
    level=BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value,
)

get_calender_info_dto = GetCalenderInfoDto(year=2021, month=7, user_id=1)


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


def test_upsert_interest_house_use_case_when_unlike_public_sales_then_success(
    session, interest_house_factory
):
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


def test_bounding_use_case_when_get_wrong_level_then_400_error(
    session, create_real_estate_with_bounding
):
    """
        level 값이 범위 밖이면 400 에러
    """
    wrong_dto = CoordinatesRangeDto(
        start_x=126.5, start_y=37.7, end_x=127.9, end_y=37.42, level=23
    )
    result = BoundingUseCase().execute(dto=wrong_dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.code == 400
    assert result.type == "level"
    assert result.message == FailureType.INVALID_REQUEST_ERROR


def test_bounding_use_case_when_get_no_coordinates_then_404_error(
    session, create_real_estate_with_bounding
):
    """
        좌표 값이 없으면(0이면) 404 에러
    """
    wrong_dto = CoordinatesRangeDto(
        start_x=0, start_y=37.7, end_x=127.9, end_y=37.42, level=15
    )
    result = BoundingUseCase().execute(dto=wrong_dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.code == 404
    assert result.type == "map_coordinates"
    assert result.message == FailureType.NOT_FOUND_ERROR


def test_bounding_use_case_when_level_is_grater_than_queryset_flag_then_call_get_bounding(
    session, create_real_estate_with_bounding
):
    """
        level 값이 BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value 이상이면
        HouseRepository().get_bounding_by_coordinates_range_dto 호출
    """
    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_bounding"
    ) as mock_get_bounding:
        mock_get_bounding.return_value = create_real_estate_with_bounding
        result = BoundingUseCase().execute(dto=coordinates_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_get_bounding.called is True
    assert result.value == mock_get_bounding.return_value


def test_bounding_use_case_when_level_is_lower_than_queryset_flag_then_call_get_administrative(
    session, create_real_estate_with_bounding
):
    """
        level 값이 BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value 미만이면
        HouseRepository().get_administrative_by_coordinates_range_dto 호출
    """
    lower_dto = CoordinatesRangeDto(
        start_x=126.5,
        start_y=37.7,
        end_x=127.9,
        end_y=37.42,
        level=BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value - 1,
    )
    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_administrative_divisions"
    ) as mock_get_bounding:
        mock_get_bounding.return_value = create_real_estate_with_bounding
        result = BoundingUseCase().execute(dto=lower_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_get_bounding.called is True
    assert result.value == mock_get_bounding.return_value


def test_get_house_public_detail_use_case_when_enable_public_sale_house(
    session, create_interest_house, create_real_estate_with_public_sale
):
    """
        사용 가능한 분양 매물이면
        HouseRepository().get_house_public_detail_by_get_house_public_detail_dto 호출
        성공시, RecentlyViewModel이 pypubsub에 의해 생성되어야 한다
    """
    get_house_public_detail_dto = GetHousePublicDetailDto(user_id=1, house_id=1)

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.is_enable_public_sale_house"
    ) as mock_enable:
        mock_enable.return_value = True
        with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_house_public_detail"
        ) as mock_house_public_detail:
            mock_house_public_detail.return_value = create_real_estate_with_public_sale[
                0
            ]
            result = GetHousePublicDetailUseCase().execute(
                dto=get_house_public_detail_dto
            )
    view_info = session.query(RecentlyViewModel).first()

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_house_public_detail.called is True
    assert mock_enable.called is True
    assert result.value == mock_house_public_detail.return_value
    assert view_info.user_id == get_house_public_detail_dto.user_id
    assert view_info.house_id == get_house_public_detail_dto.house_id


def test_get_house_public_detail_use_case_when_disable_public_sale_house(
    session, create_interest_house, create_real_estate_with_public_sale
):
    """
        사용 불가능한 분양 매물이면 404 에러
    """
    get_house_public_detail_dto = GetHousePublicDetailDto(user_id=1, house_id=1)

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.is_enable_public_sale_house"
    ) as mock_disable:
        mock_disable.return_value = False
        with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_house_public_detail"
        ) as mock_house_public_detail:
            mock_house_public_detail.return_value = create_real_estate_with_public_sale[
                0
            ]
            result = GetHousePublicDetailUseCase().execute(
                dto=get_house_public_detail_dto
            )

    assert isinstance(result, UseCaseFailureOutput)
    assert mock_house_public_detail.called is False
    assert mock_disable.called is True
    assert result.message == FailureType.NOT_FOUND_ERROR


def test_get_calender_info_use_case_when_included_request_date(
    session, create_real_estate_with_public_sale
):
    """
        get_calender_info_by_get_calender_info_dto -> return mocking
        요청 받은 년월에 속한 매물이 있으면 캘린더 정보 리턴
    """
    public_sale_calender = PublicSaleCalenderEntity(
        id=1,
        real_estate_id=1,
        name="힐스테이트",
        offer_date="20210705",
        subscription_start_date="20210705",
        subscription_end_date="20210705",
        special_supply_date="20210705",
        special_supply_etc_date="20210705",
        first_supply_date="20210705",
        first_supply_etc_date="20210705",
        second_supply_date="20210705",
        second_supply_etc_date="20210705",
        notice_winner_date="20210705",
        contract_start_date="20210705",
        contract_end_date="20210705",
        move_in_year=2023,
        move_in_month=12,
    )
    sample_calender_info = CalenderInfoEntity(
        is_like=True,
        id=1,
        name="힐스테이트",
        road_address="서울 서초구 어딘가",
        jibun_address="서울 서초구 어딘가",
        public_sale=public_sale_calender,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_calender_info"
    ) as mock_calender_info:
        mock_calender_info.return_value = sample_calender_info
        result = GetCalenderInfoUseCase().execute(dto=get_calender_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_calender_info.called is True


def test_get_calender_info_use_case_when_no_included_request_date(
    session, create_real_estate_with_public_sale
):
    """
        get_calender_info_by_get_calender_info_dto -> return mocking
        요청 받은 년월에 속한 매물이 없으면 null 리턴
    """
    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_calender_info"
    ) as mock_calender_info:
        mock_calender_info.return_value = None
        result = GetCalenderInfoUseCase().execute(dto=get_calender_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value == "null"
    assert mock_calender_info.called is True


def test_get_interest_house_list_use_case_when_like_one_public_sale_then_result_one(
    session, create_users, create_real_estate_with_public_sale
):
    dto = GetUserDto(user_id=create_users[0].id)
    result = GetInterestHouseListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, list)
    assert len(result.value) == 1
    assert result.value[0].house_id == 1


def test_get_interest_house_list_use_case_when_like_one_public_sale_then_result_zero(
    session, create_users
):
    dto = GetUserDto(user_id=create_users[0].id)
    result = GetInterestHouseListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, list)
    assert len(result.value) == 0


def test_get_recent_view_list_use_case_when_watch_recently_view_then_result_one(
    session,
    create_users,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
):
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)
    session.add(public_sale_photo)
    session.commit()

    dto = GetUserDto(user_id=create_users[0].id)
    result = GetRecentViewListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, list)
    assert len(result.value) == 1
    assert result.value[0].image_path == public_sale_photo.path
