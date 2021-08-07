from enum import Enum


class BannerSectionType(Enum):
    """
        사용 테이블: banners
        용도 : 배너 이미지를 내려줄때, 화면 구분용
    """

    HOME_SCREEN = 0
    PRE_SUBSCRIPTION_INFO = 1


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


class ButtonSectionType(Enum):
    """
        사용 테이블: banners
        용도 : 버튼 링크 URL 내려줄때, 화면 구분용
    """

    HOME_SCREEN = 0
    PRE_SUBSCRIPTION_INFO = 1
