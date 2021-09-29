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


class CalendarYearThreshHold(Enum):
    """
        사용처 : house_calendar_list_view(),
               GetCalendarInfoReqestSchema
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


class SectionType(Enum):
    """
        사용 테이블: banners, button_links
        용도 : 배너 이미지를 내려줄때, 버튼 링크 URL 내려줄때 화면 구분용
    """

    HOME_SCREEN = 0
    PRE_SUBSCRIPTION_INFO = 1
    PUBLIC_SALE_DETAIL = 2


class BannerSubTopic(Enum):
    """
        사용 테이블: banners
        용도 : 배너 소주제 구분용
    """

    # 홈 화면
    HOME_THIRD_PLANNED_CITY = 0
    HOME_SUBSCRIPTION_BY_REGION = 1
    HOME_SUBSCRIPTION_GUIDE = 2

    # 사전청약 알아보기 화면
    PRE_SUBSCRIPTION_MAP = 3
    PRE_SUBSCRIPTION_CITIES = 4
    PUBLIC_SALE = 5
    HONEYMOON_HOPE_TOWN = 6
    PRE_SUBSCRIPTION_FAQ = 7

    # 공통
    TOP_SCREEN_BANNER = 8
    BOTTOM_SCREEN_BANNER = 9


class PricePerMeterEnum(Enum):
    """
        평당가격 계산할 때 사용
    """

    CALC_VAR = 3.3058


class BoundingDegreeEnum(Enum):
    """
        반경 내 매물 검색시 사용할 반경 값(단위: 도)
        <degree> -> 반경이 넓어지면 쿼리 속도가 느려집니다
        1도 : 111km
        0.1도 : 11.11km
        0.01도 : 1.11km
        0.001도 : 111m
    """

    DEGREE = 0.01


class PublicSaleStatusEnum(Enum):
    """
        사용 모델 : 분양 테이블
        사용 목적 : 지도 바운딩시 상태 표시
        UNKNOWN : 알 수 없음 (값이 없거나 잘못된 값)
        BEFORE_OPEN : 분양 예정
        IS_RECEIVING : 분양중/접수중
        IS_CLOSED : 마감됨
    """

    UNKNOWN = 0
    BEFORE_OPEN = 1
    IS_RECEIVING = 2
    IS_CLOSED = 3
