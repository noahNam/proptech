from enum import Enum


class RealTradeTypeEnum(Enum):
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
