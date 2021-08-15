from unittest.mock import patch

from app.persistence.model import InterestHouseModel, RecentlyViewModel
from core.domains.house.dto.house_dto import (
    UpsertInterestHouseDto,
    CoordinatesRangeDto,
    GetHousePublicDetailDto,
    GetCalendarInfoDto,
    GetSearchHouseListDto,
    BoundingWithinRadiusDto,
    SectionTypeDto,
    GetHouseMainDto,
)
from core.domains.house.entity.house_entity import (
    SearchRealEstateEntity,
    SearchPublicSaleEntity,
    SearchAdministrativeDivisionEntity,
    GetSearchHouseListEntity,
    GetMainPreSubscriptionEntity,
    GetHouseMainEntity,
    DetailCalendarInfoEntity,
    SimpleCalendarInfoEntity,
    PublicSaleDetailCalendarEntity,
    PublicSaleSimpleCalendarEntity,
)
from core.domains.house.enum.house_enum import (
    HouseTypeEnum,
    BoundingLevelEnum,
    SearchTypeEnum,
    SectionType,
    BannerSubTopic,
    PreSaleTypeEnum,
)
from core.domains.house.use_case.v1.house_use_case import (
    UpsertInterestHouseUseCase,
    BoundingUseCase,
    GetHousePublicDetailUseCase,
    GetCalendarInfoUseCase,
    GetInterestHouseListUseCase,
    GetRecentViewListUseCase,
    GetSearchHouseListUseCase,
    BoundingWithinRadiusUseCase,
    GetMainPreSubscriptionUseCase,
    GetHouseMainUseCase,
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

get_calendar_info_dto = GetCalendarInfoDto(year=2021, month=7, user_id=1)


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


def test_get_calendar_info_use_case_when_included_request_date(
    session, create_real_estate_with_public_sale
):
    """
        get_calendar_info_by_get_calendar_info_dto -> return mocking
        요청 받은 년월에 속한 매물이 있으면 캘린더 정보 리턴
    """
    public_sale_detail_calendar = PublicSaleDetailCalendarEntity(
        id=1,
        real_estate_id=1,
        name="힐스테이트",
        trade_type=PreSaleTypeEnum.PRE_SALE,
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
    sample_calendar_info = DetailCalendarInfoEntity(
        is_like=True,
        id=1,
        name="힐스테이트",
        road_address="서울 서초구 어딘가",
        jibun_address="서울 서초구 어딘가",
        public_sale=public_sale_detail_calendar,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_detail_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = sample_calendar_info
        result = GetCalendarInfoUseCase().execute(dto=get_calendar_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_calendar_info.called is True


def test_get_calendar_info_use_case_when_no_included_request_date(
    session, create_real_estate_with_public_sale
):
    """
        get_calendar_info_by_get_detail_calendar_info_dto -> return mocking
        요청 받은 년월에 속한 매물이 없으면 null 리턴
    """
    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_detail_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = None
        result = GetCalendarInfoUseCase().execute(dto=get_calendar_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value is None
    assert mock_calendar_info.called is True


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


def test_get_search_house_list_use_case_when_no_keywords_then_return_none(session):
    dto = GetSearchHouseListDto(keywords="")
    result = GetSearchHouseListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value is None


def test_get_search_house_list_use_case_when_less_then_1_keywords_then_return_none(
    session,
):
    dto = GetSearchHouseListDto(keywords="글")
    result = GetSearchHouseListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value is None


def test_get_search_house_list_use_case_when_right_keywords_then_return_search_result(
    session, create_real_estate_with_public_sale
):
    """
        search_result : mocking
    """
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
        result = GetSearchHouseListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_search.called is True
    assert dto.keywords in result.value.real_estates[0].jibun_address
    assert dto.keywords in result.value.public_sales[0].name
    assert dto.keywords in result.value.administrative_divisions[0].name


def test_bounding_within_radius_use_case_when_wrong_search_type_then_fail(session):
    dto = BoundingWithinRadiusDto(house_id=1, search_type=4)

    result = BoundingWithinRadiusUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseFailureOutput)


def test_bounding_within_radius_use_case_when_no_coordinates_then_fail(session):
    """
        get_geometry_coordinates_from_administrative_division() -> mocking
    """
    dto = BoundingWithinRadiusDto(
        house_id=1, search_type=SearchTypeEnum.FROM_ADMINISTRATIVE_DIVISION.value
    )
    with patch(
        "core.domains.house.repository.house_repository"
        ".HouseRepository.get_geometry_coordinates_from_administrative_division"
    ) as mock_get:
        mock_get.return_value = None
        result = BoundingWithinRadiusUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert mock_get.called is True


def test_bounding_within_radius_use_case_when_get_coordinates_then_success(
    session, create_real_estate_with_bounding
):
    """
        result: mocking
    """
    dto = BoundingWithinRadiusDto(
        house_id=1, search_type=SearchTypeEnum.FROM_REAL_ESTATE.value
    )

    mock_output = UseCaseSuccessOutput()
    mock_output.value = create_real_estate_with_bounding
    with patch(
        "core.domains.house.use_case.v1.house_use_case"
        ".BoundingWithinRadiusUseCase.execute"
    ) as mock_result:
        mock_result.return_value = mock_output
        result = BoundingWithinRadiusUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_result.called is True


def test_when_get_house_main_use_case_then_include_present_calendar_info(
    session, create_users, banner_factory
):
    """
        get_calendar_info_by_get_simple_calendar_info_dto -> return mocking
    """
    banner1 = banner_factory(
        banner_image=True,
        section_type=SectionType.HOME_SCREEN.value,
        sub_topic=BannerSubTopic.HOME_THIRD_PLANNED_CITY.value,
    )
    banner2 = banner_factory(
        banner_image=True,
        section_type=SectionType.HOME_SCREEN.value,
        sub_topic=BannerSubTopic.HOME_SUBSCRIPTION_BY_REGION.value,
    )

    session.add_all([banner1, banner2])
    session.commit()

    public_sale_simple_calendar = PublicSaleSimpleCalendarEntity(
        id=1,
        real_estate_id=1,
        name="힐스테이트",
        trade_type=PreSaleTypeEnum.PRE_SALE,
        subscription_start_date="20210705",
        subscription_end_date="20210705",
        special_supply_date="20210705",
        special_supply_etc_date="20210705",
        first_supply_date="20210705",
        first_supply_etc_date="20210705",
        second_supply_date="20210705",
        second_supply_etc_date="20210705",
        notice_winner_date="20210705",
    )
    sample_calendar_info = SimpleCalendarInfoEntity(
        is_like=True,
        id=1,
        name="힐스테이트",
        road_address="서울 서초구 어딘가",
        jibun_address="서울 서초구 어딘가",
        public_sale=public_sale_simple_calendar,
    )

    dto = GetHouseMainDto(
        section_type=SectionType.HOME_SCREEN.value, user_id=create_users[0].id
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_simple_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = [sample_calendar_info]
        result = GetHouseMainUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, GetHouseMainEntity)
    assert mock_calendar_info.called is True
    assert len(result.value.banner_list) == 2


def test_when_get_home_banner_use_case_with_wrong_section_type_then_fail(
    session, create_users
):
    invalid_dto = GetHouseMainDto(
        section_type=SectionType.PRE_SUBSCRIPTION_INFO.value, user_id=create_users[0].id
    )
    result = GetHouseMainUseCase().execute(dto=invalid_dto)

    assert isinstance(result, UseCaseFailureOutput)


def test_when_get_pre_subscription_banner_use_case_then_return_pre_subscription_banner_info_with_button_links(
    session, create_users, button_link_factory, banner_factory
):
    banner1 = banner_factory(
        banner_image=True,
        section_type=SectionType.PRE_SUBSCRIPTION_INFO.value,
        sub_topic=BannerSubTopic.PRE_SUBSCRIPTION_FAQ.value,
    )
    banner2 = banner_factory(
        banner_image=True,
        section_type=SectionType.PRE_SUBSCRIPTION_INFO.value,
        sub_topic=BannerSubTopic.PRE_SUBSCRIPTION_FAQ.value,
    )

    button1 = button_link_factory(section_type=SectionType.PRE_SUBSCRIPTION_INFO.value)
    button2 = button_link_factory(section_type=SectionType.PRE_SUBSCRIPTION_INFO.value)

    session.add_all([banner1, banner2, button1, button2])
    session.commit()

    dto = SectionTypeDto(section_type=SectionType.PRE_SUBSCRIPTION_INFO.value)

    result = GetMainPreSubscriptionUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, GetMainPreSubscriptionEntity)
    assert len(result.value.banner_list) == 2
    assert len(result.value.button_links) == 2


def test_when_get_pre_subscription_banner_use_case_with_wrong_section_type_then_fail(
    session,
):
    invalid_dto = SectionTypeDto(section_type=SectionType.HOME_SCREEN.value)
    result = GetMainPreSubscriptionUseCase().execute(dto=invalid_dto)

    assert isinstance(result, UseCaseFailureOutput)
