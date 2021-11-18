from enum import Enum


class PostCategoryEnum(Enum):
    """
        사용 테이블 : posts
        용도 : 공지사항, 게시판, 청약가이드 등 게시글 제목
    """

    NOTICE = 0
    FAQ = 1
    SUBSCRIPTION_FAQ = 2
    SUBSCRIPTION_WORDS = 3
    ABOUT_SUBSCRIPTION = 4
    # 전세 계약시 주의사항
    ABOUT_LOAN_SECTION_PAGE_1 = 5
    # 경쟁률 예측 페이지
    PREDICT_COMPETITION_CONTENTS = 6
    # 청년 대출 비교
    ABOUT_LOAN_SECTION_PAGE_2 = 7
    # 전세자금대출 비교
    ABOUT_LOAN_SECTION_PAGE_3 = 8


class PostCategoryDetailEnum(Enum):
    """
        사용 테이블 : posts
        용도 : 게시글의 소주제별 카테고리
        (FAQ - 계정/인증, 개인정보, 사용법, 환경설정)
    """

    # 공지사항, 청약용어, 대출은이렇게_배너(1,2,3)
    NO_DETAIL = 0

    # FAQ
    ALL_LIST = 1
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


class PostLimitEnum(Enum):
    """
        용도 : 공지사항 Post pagination
    """

    LIMIT = 20


class PostOnlyImageEnum(Enum):
    """
        용도 : post request 시, 이미지 path 만 엔티티로 받고 싶을 때 파라미터 검증시 사용
    """

    NO = 0
    YES = 1
