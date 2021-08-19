from enum import Enum


class PostCategoryEnum(Enum):
    """
        사용 테이블 : posts
        용도 : 공지사항, 게시판, 청약가이드 등 게시글 제목
    """

    NOTICE = 0
    FAQ = 1
    SUBSCRIPTION_FAQ = 2
    SUBSCRIPTION_GUIDE = 3
    SUBSCRIPTION_WORDS = 4
    ABOUT_SUBSCRIPTION = 5


class PostCategoryDetailEnum(Enum):
    """
        사용 테이블 : posts
        용도 : 게시글의 소주제별 카테고리
        (FAQ - 계정/인증, 개인정보, 사용법, 환경설정)
    """

    # 공지사항, 청약용어
    NO_DETAIL = 0

    # FAQ
    ACCOUNT_AUTH = 1
    PERSONAL_INFO = 2
    HOW_TO_USE = 3
    SETTINGS = 4

    # 청약 FAQ, 청약 가이드
    SUBSCRIPTION_CREDENTIAL = 5
    GENERAL_SUPPLY = 6
    SPECIAL_SUPPLY = 7
    INCOME_STANDARD = 8


class PostTypeEnum(Enum):
    """
        사용 테이블 : post_attachments
    """

    PHOTO = 0
    MEDIA = 1
