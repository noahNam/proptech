import os
from enum import Enum


class PromotionTypeEnum(Enum):
    """
        사용모델 : PromotionModel
    """

    ALL = "all"
    SOME = "some"


class PromotionDivEnum(Enum):
    """
        사용모델 : PromotionModel
    """

    HOUSE = "house"
    USER = "user"


class TicketSignEnum(Enum):
    """
        사용모델 : TicketModel
    """

    PLUS = "plus"
    MINUS = "minus"


class TicketTypeDivisionEnum(Enum):
    """
        사용모델 : TicketModel
        sign (+)
            SURVEY_PROMOTION -> 유저 설문 완료시 티켓을 공짜로 주는 프로모션
            SHARE_PROMOTION -> 추천 코드 공유시 티켓을 공짜로 주는 프로모션
            CHARGED -> 결제로 인해 쌓이는 티켓
        sign (-)
            REFUND -> 티켓 환불
            USED_TICKET_TO_HOUSE -> 티켓 사용
            USED_TICKET_TO_USER -> 티켓 사용

            USED_PROMOTION_TO_HOUSE -> 프로모션 사용
            USED_PROMOTION_TO_USER -> 프로모션 사용
                amount = 0 처리
                프르모션 적용으로 티켓을 사용안할 때도 내역 쌓아야 함.
                -> ticket_usage_results.ticket_id update에 필요
    """

    SURVEY_PROMOTION = 1
    SHARE_PROMOTION = 2
    CHARGED = 3
    REFUND = 4
    USED_TICKET_TO_HOUSE = 5
    USED_TICKET_TO_USER = 6
    USED_PROMOTION_TO_HOUSE = 7
    USED_PROMOTION_TO_USER = 8


class RecommendCodeMaxCountEnum(Enum):
    """
        사용모델 : RecommendCodeModel
        추천코드 만료 사용 횟수
    """

    MAX_COUNT = 2


class CallJarvisEnum(Enum):
    JARVIS_BASE_URL = os.environ.get("JARVIS_BASE_URL")
    CALL_PREDICT_HOUSE = "/api/jarvis/v1/predicts/house"
    CALL_PREDICT_USER = "/api/jarvis/v1/predicts/user"
