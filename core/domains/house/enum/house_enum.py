from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


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
    PUBLIC_TRADE = "분양권매매"
    RENT_TRADE = "임대매매"
    LONG_TERM_RENT = "전세"
    MONTHLY_RENT = "월세"
    PRIVATE_TRADE = "입주권매매"


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

        <Request Parameter>
        [16 ~ 21 level range] (BoundingPresenter()) -> 부동산
        level < SELECT_QUERYSET_FLAG_LEVEL -> BoundingAdministrativePresenter() else BoundingPresenter()

        [13 ~ 15 level range] (BoundingAdministrativePresenter())
        MAX_SI_GUN_GU_LEVEL < level -> Level_3 : 읍, 면, 동, 리

        [11 ~ 12 level range]
        MIN_SI_GUN_GU_LEVEL <= level <= MAX_SI_GUN_GU_LEVEL -> Level_2 : 시, 군, 구

        [8 ~ 10 level range]
        level < MIN_SI_GUN_GU_LEVEL -> Level_1 : 광역시, 특별시, 도
    """

    SELECT_QUERYSET_FLAG_LEVEL = 16
    MIN_SI_GUN_GU_LEVEL = 11
    MAX_SI_GUN_GU_LEVEL = 12
    MAX_NAVER_MAP_API_ZOOM_LEVEL = 21
    MIN_NAVER_MAP_API_ZOOM_LEVEL = 8


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
    PREDICT_COMPETITION = 3


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

    # 대출
    HOME_LOAN_BANNER = 11


class CalcPyoungEnum(Enum):
    """
        CALC_VAR : 평수 구할 때 사용하는 상수
        TEMP_CALC_VAR : 전용면적으로 평수를 구할때 사용하는 상수
        AVG_DEFAULT_PYOUNG : 클러스터링시 보여주는 평수가 몇평 기준인지를 나타내는 상수
    """

    CALC_VAR = 3.3058
    TEMP_CALC_VAR = 1.37
    AVG_DEFAULT_PYOUNG = 34


class BoundingDegreeEnum(Enum):
    """
        반경 내 매물 검색시 사용할 반경 값(단위: 도)
        <degree> -> 반경이 넓어지면 쿼리 속도가 느려집니다
        1도 : 111km
        0.1도 : 11.11km
        0.01도 : 1.11km
        0.001도 : 111m
    """

    DEGREE = 0.1


class PublicSaleStatusEnum(ExtendedEnum):
    """
        사용 모델 : 분양 테이블
        사용 목적 : 지도 바운딩시 상태 표시
        UNKNOWN : 알 수 없음 (값이 없거나 잘못된 값)
        BEFORE_OPEN : 분양 예정
        IS_RECEIVING : 분양중/접수중
        IS_CLOSED : 마감됨/분양완료
    """

    UNKNOWN = 0
    BEFORE_OPEN = 1
    IS_RECEIVING = 2
    IS_CLOSED = 3


class BoundingIncludePrivateEnum(ExtendedEnum):
    """
    사용 모델 : PrivateSaleModel
    사용 목적 : 지도 바운딩시 실거래가 표시 유무
            NOT_INCLUDE: 미포함
            INCLUDE: 포함
    """

    NOT_INCLUDE = 0
    INCLUDE = 1


class BoundingPrivateTypeEnum(ExtendedEnum):
    """
    사용 모델 : PrivateSaleModel
    사용 목적 : 지도 바운딩시 받는 파라미터 표시
            APT_ONLY: 아파트만 필터
            OP_ONLY : 오피스텔만 필터
    """

    APT_ONLY = 1
    OP_ONLY = 2


class BoundingPublicTypeEnum(Enum):
    """
    사용 모델 : PublicSaleModel
    사용 목적 : 지도 바운딩시 받는 파라미터 표시
            NOTHING: 아무것도 표시 안함
            PUBLIC_ONLY: 국민분양만 필터
            PRIVATE_ONLY: 민영분양만 필터
            ALL_PRE_SALE: 국민 민영 분양 모두 필터
    """

    NOTHING = 0
    PUBLIC_ONLY = 1
    PRIVATE_ONLY = 2
    ALL_PRE_SALE = 3


class PrivateSaleContractStatusEnum(Enum):
    """
    사용 모델 : PrivateSaleModel
    사용 목적 : house_worker_use_case -> 3개월 이내 거래여부 판별
            NOTHING: 거래 없음
            LONG_AGO: 현재 날짜로부터 3개월 이후에 오래된 거래가 있음
            RECENT_CONTRACT: 현재 날짜로부터 3개월 이전 기간에 거래가 있음
    """

    NOTHING = 0
    LONG_AGO = 1
    RECENT_CONTRACT = 2


class ReplacePublicToPrivateSalesEnum(Enum):
    """
        사용 모델 : PublicSales
        사용 목적 : house_worker_use_case -> 매매 전환 대상 여부 판별
                NO: 매매 전환 대상 아님
                YES: 매매 전환 대상
                UNKNOWN: 값이 없거나 잘못되어 알 수 없음
    """

    NO = 0
    YES = 1
    UNKNOWN = 2
