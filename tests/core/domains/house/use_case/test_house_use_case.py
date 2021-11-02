from unittest.mock import patch

from app.extensions.utils.house_helper import HouseHelper
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
    GetSearchHouseListEntity,
    GetMainPreSubscriptionEntity,
    GetHouseMainEntity,
    SimpleCalendarInfoEntity,
    PublicSaleSimpleCalendarEntity,
    HousePublicDetailEntity,
    MainRecentPublicInfoEntity,
    PublicSaleEntity,
    PublicSaleDetailEntity,
)
from core.domains.house.enum.house_enum import (
    HouseTypeEnum,
    BoundingLevelEnum,
    SearchTypeEnum,
    SectionType,
    BannerSubTopic,
    PreSaleTypeEnum,
    PublicSaleStatusEnum,
    BoundingPrivateTypeEnum,
    BoundingPublicTypeEnum,
    BoundingIncludePrivateEnum,
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
    user_id=1,
    start_x=126.5,
    start_y=37.7,
    end_x=127.9,
    end_y=37.42,
    level=BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value,
    private_type=BoundingPrivateTypeEnum.APT_ONLY.value,
    public_type=BoundingPublicTypeEnum.PUBLIC_ONLY.value,
    include_private=BoundingIncludePrivateEnum.INCLUDE.value,
)


get_calendar_info_dto = GetCalendarInfoDto(year=2021, month=7, user_id=1)


def test_upsert_interest_house_use_case_when_like_public_sales_then_success(
    session, create_real_estate_with_public_sale
):
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
    session, interest_house_factory, create_real_estate_with_public_sale
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
        user_id=1,
        start_x=126.5,
        start_y=37.7,
        end_x=127.9,
        end_y=37.42,
        level=23,
        private_type=BoundingPrivateTypeEnum.APT_ONLY.value,
        public_type=BoundingPublicTypeEnum.PUBLIC_ONLY.value,
        include_private=BoundingIncludePrivateEnum.INCLUDE.value,
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
        user_id=1,
        start_x=0,
        start_y=37.7,
        end_x=127.9,
        end_y=37.42,
        level=15,
        private_type=BoundingPrivateTypeEnum.APT_ONLY.value,
        public_type=BoundingPublicTypeEnum.PUBLIC_ONLY.value,
        include_private=BoundingIncludePrivateEnum.INCLUDE.value,
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
        user_id=1,
        start_x=126.5,
        start_y=37.7,
        end_x=127.9,
        end_y=37.42,
        level=BoundingLevelEnum.SELECT_QUERYSET_FLAG_LEVEL.value - 1,
        private_type=BoundingPrivateTypeEnum.APT_ONLY.value,
        public_type=BoundingPublicTypeEnum.PUBLIC_ONLY.value,
        include_private=BoundingIncludePrivateEnum.INCLUDE.value,
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
    session,
    create_interest_house,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
    public_sale_factory,
):
    """
        사용 가능한 분양 매물이면
        HouseRepository().get_house_with_public_sales 호출
        성공시, RecentlyViewModel이 pypubsub에 의해 생성되어야 한다
    """
    get_house_public_detail_dto = GetHousePublicDetailDto(user_id=1, house_id=1)

    public_sales = public_sale_factory.build(public_sale_details=True)
    public_sale_photo_1 = public_sale_photo_factory.build(id=1, public_sales_id=1)
    public_sale_photo_2 = public_sale_photo_factory.build(id=2, public_sales_id=1)
    session.add(public_sale_photo_1, public_sale_photo_2)
    session.commit()

    detail_entity = PublicSaleDetailEntity(
        id=public_sales.public_sale_details[0].id,
        public_sales_id=public_sales.public_sale_details[0].public_sales_id,
        private_area=public_sales.public_sale_details[0].private_area,
        private_pyoung_number=10,
        supply_area=public_sales.public_sale_details[0].supply_area,
        supply_pyoung_number=20,
        supply_price=public_sales.public_sale_details[0].supply_price,
        acquisition_tax=public_sales.public_sale_details[0].acquisition_tax,
        area_type="84A",
        special_household=public_sales.public_sale_details[0].special_household,
        general_household=public_sales.public_sale_details[0].general_household,
        total_household=public_sales.public_sale_details[0].total_household,
    )

    public_sales_entity = PublicSaleEntity(
        id=public_sales.id,
        real_estate_id=public_sales.real_estate_id,
        name=public_sales.name,
        region=public_sales.region,
        housing_category=public_sales.housing_category,
        rent_type=public_sales.rent_type,
        trade_type=public_sales.trade_type,
        construct_company=public_sales.construct_company,
        supply_household=public_sales.supply_household,
        is_available=public_sales.is_available,
        offer_date=public_sales.offer_date,
        offer_notice_url=public_sales.offer_notice_url,
        subscription_start_date=public_sales.subscription_start_date,
        subscription_end_date=public_sales.subscription_end_date,
        status=HouseHelper().public_status(
            offer_date=public_sales.offer_date,
            subscription_end_date=public_sales.subscription_end_date,
        ),
        special_supply_date=public_sales.special_supply_date,
        special_supply_etc_date=public_sales.special_supply_etc_date,
        special_etc_gyeonggi_date=public_sales.special_etc_gyeonggi_date,
        first_supply_date=public_sales.first_supply_date,
        first_supply_etc_date=public_sales.first_supply_etc_date,
        first_etc_gyeonggi_date=public_sales.first_etc_gyeonggi_date,
        second_supply_date=public_sales.second_supply_date,
        second_supply_etc_date=public_sales.second_supply_etc_date,
        second_etc_gyeonggi_date=public_sales.second_etc_gyeonggi_date,
        notice_winner_date=public_sales.notice_winner_date,
        contract_start_date=public_sales.contract_start_date,
        contract_end_date=public_sales.contract_end_date,
        move_in_year=public_sales.move_in_year,
        move_in_month=public_sales.move_in_month,
        min_down_payment=public_sales.min_down_payment,
        max_down_payment=public_sales.max_down_payment,
        down_payment_ratio=public_sales.down_payment_ratio,
        reference_url=public_sales.reference_url,
        created_at=public_sales.created_at,
        updated_at=public_sales.updated_at,
        public_sale_photos=[
            public_sale_photo_1.to_entity(),
            public_sale_photo_2.to_entity(),
        ],
        public_sale_details=[detail_entity],
    )

    mock_entity = HousePublicDetailEntity(
        id=1,
        name="분양아파트",
        road_address="서울시 어딘가",
        jibun_address="서울시 어딘가",
        si_do="서울특별시",
        si_gun_gu="서초구",
        dong_myun="어딘가",
        ri="-",
        road_name="어딘가1길",
        road_number="10",
        land_number="123-1",
        is_available=True,
        latitude=127,
        longitude=37.71,
        is_like=True,
        min_pyoung_number=25,
        max_pyoung_number=32,
        min_supply_area=84.0,
        max_supply_area=112.0,
        avg_supply_price=50000,
        supply_price_per_pyoung=123,
        min_acquisition_tax=100000,
        max_acquisition_tax=200000,
        public_sales=public_sales_entity,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.is_enable_public_sale_house"
    ) as mock_enable:
        mock_enable.return_value = True
        with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_house_with_public_sales"
        ) as mock_house_public_detail:
            mock_house_public_detail.return_value = create_real_estate_with_public_sale
            with patch(
                "core.domains.house.repository.house_repository.HouseRepository.make_house_public_detail_entity"
            ) as mock_result:
                mock_result.return_value = mock_entity
                result = GetHousePublicDetailUseCase().execute(
                    dto=get_house_public_detail_dto
                )
    view_info = session.query(RecentlyViewModel).first()

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_house_public_detail.called is True
    assert mock_enable.called is True
    assert result.value == mock_result.return_value
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
            "core.domains.house.repository.house_repository.HouseRepository.get_house_with_public_sales"
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
    public_sale_simple_calendar = PublicSaleSimpleCalendarEntity(
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
    sample_calendar_info = SimpleCalendarInfoEntity(
        is_like=True,
        id=1,
        name="힐스테이트",
        road_address="서울 서초구 어딘가",
        jibun_address="서울 서초구 어딘가",
        public_sale=public_sale_simple_calendar,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_simple_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = sample_calendar_info
        result = GetCalendarInfoUseCase().execute(dto=get_calendar_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_calendar_info.called is True


def test_get_calendar_info_use_case_when_no_included_request_date(
    session, create_real_estate_with_public_sale
):
    """
        get_calendar_info_by_get_simple_calendar_info_dto -> return mocking
        요청 받은 년월에 속한 매물이 없으면 null 리턴
    """
    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_simple_calendar_info"
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
    assert public_sale_photo.path in result.value[0].image_path


def test_get_search_house_list_use_case_when_no_keywords_then_return_none(
    session, create_users
):
    dto = GetSearchHouseListDto(keywords="", user_id=create_users[0].id)
    result = GetSearchHouseListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value == []


def test_get_search_house_list_use_case_when_less_then_1_keywords_then_return_none(
    session, create_users
):
    dto = GetSearchHouseListDto(keywords="글", user_id=create_users[0].id)
    result = GetSearchHouseListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value == []


def test_get_search_house_list_use_case_when_right_keywords_then_return_search_result(
    session,
    create_users,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
):
    """
        search_result : mocking
    """
    dto = GetSearchHouseListDto(keywords="서울", user_id=create_users[0].id)
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)
    session.add(public_sale_photo)
    session.commit()

    mock_result = GetSearchHouseListEntity(
        house_id=1,
        jibun_address="서울시 서초구 어딘가",
        name="반포자이",
        is_like=False,
        image_path=public_sale_photo.path,
        subscription_start_date="20210901",
        subscription_end_date="202109018",
        status=PublicSaleStatusEnum.IS_CLOSED.value,
        avg_down_payment=100000.75,
        avg_supply_price=200000.23,
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_search_house_list"
    ) as mock_search:
        mock_search.return_value = mock_result
        result = GetSearchHouseListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert mock_search.called is True


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
    session,
    create_users,
    banner_factory,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
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
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)

    session.add_all([banner1, banner2, public_sale_photo])
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

    sample_recent_public_info = MainRecentPublicInfoEntity(
        id=1,
        name="힐스테이트",
        si_do="서울특별시",
        status=3,
        public_sale_photos=[public_sale_photo.to_entity()],
    )

    dto = GetHouseMainDto(
        section_type=SectionType.HOME_SCREEN.value, user_id=create_users[0].id
    )

    with patch(
        "core.domains.house.repository.house_repository.HouseRepository.get_simple_calendar_info"
    ) as mock_calendar_info:
        mock_calendar_info.return_value = [sample_calendar_info]
        with patch(
            "core.domains.house.repository.house_repository.HouseRepository.get_main_recent_public_info_list"
        ) as recent_public_list:
            recent_public_list.return_value = create_real_estate_with_public_sale
            with patch(
                "core.domains.house.use_case.v1.house_use_case.GetHouseMainUseCase._make_recent_public_info_entity"
            ) as recent_public_infos:
                recent_public_infos.return_value = [sample_recent_public_info]
                result = GetHouseMainUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, GetHouseMainEntity)
    assert mock_calendar_info.called is True
    assert recent_public_infos.called is True
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
