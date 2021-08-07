from enum import Enum


class HouseTypeEnum(Enum):
    """
        사용모델 : InterestHouseModel, RecentlyViewModel
    """

    PUBLIC_SALES = 1
    PRIVATE_SALES = 2


class RealTradeTypeEnum(Enum):
    """
        사용 모델 : 실거래가 테이블
    """

    TRADING = "매매"
    LONG_TERM_RENT = "전세"
    MONTHLY_RENT = "월세"


class BuildTypeEnum(Enum):
    """
        사용 모델 : 실거래가 테이블
    """

    APARTMENT = "아파트"
    STUDIO = "오피스텔"
    ROW_HOUSE = "연립다세대"


class HousingCategoryEnum(Enum):
    """
        사용 모델 : 분양 테이블
    """

    PUBLIC = "국민"
    PRIVATE = "민영"


class RentTypeEnum(Enum):
    """
        사용 모델 : 분양 테이블
    """

    PRE_SALE = "분양"
    RENTAL = "임대"


class PreSaleTypeEnum(Enum):
    """
        사용 모델 : 분양 테이블
    """

    PRE_SALE = "분양"
    PRE_SUBSCRIPTION = "사전청약"


class DivisionLevelEnum(Enum):
    """
        사용 모델 : 행정구역 테이블
        Level_1 : 광역시, 특별시, 도
        Level_2 : 시, 군, 구
        Level_3 : 읍, 면, 동, 리
    """

    LEVEL_1 = "1"
    LEVEL_2 = "2"
    LEVEL_3 = "3"


class BoundingLevelEnum(Enum):
    """
        사용처 : bounding_view(),
               BoundingUseCase,
               HouseRepository - get_administrative_queryset_by_coordinates_range_dto()
        목적: bounding level 조건에 따라 쿼리 필터 조정
    """

    SELECT_QUERYSET_FLAG_LEVEL = 15
    MIN_SI_GUN_GU_LEVEL = 9
    MAX_SI_GUN_GU_LEVEL = 11
    MAX_NAVER_MAP_API_ZOOM_LEVEL = 22
    MIN_NAVER_MAP_API_ZOOM_LEVEL = 6


class calendarYearThreshHold(Enum):
    """
        사용처 : house_calendar_list_view(),
               GetcalendarInfoReqestSchema
        목적 : 파라미터 year 값의 범위 제한
    """

    MIN_YEAR = 2017
    MAX_YEAR = 2030


class SearchTypeEnum(Enum):
    """
        사용처 : get_bounding_within_radius_view(),
               GetBoundingWithinRadiusSchema
        목적 : 파라미터 search_type 값의 범위 제한
    """

    FROM_REAL_ESTATE = 1
    FROM_PUBLIC_SALE = 2
    FROM_ADMINISTRATIVE_DIVISION = 3
