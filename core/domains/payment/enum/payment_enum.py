from enum import Enum


class PromotionTypeEnum(Enum):
    """
        사용모델 : PromotionModel
    """

    ALL = "all"
    SOME = "some"


class TicketSignEnum(Enum):
    """
        사용모델 : TicketModel
    """

    PLUS = "plus"
    MINUS = "minus"


class TicketTypeDivisionEnum(Enum):
    """
        사용모델 : TicketTypeModel
        sign (+)
            SURVEY_PROMOTION -> 유저 설문 완료시 티켓을 공짜로 주는 프로모션
            SHARE_PROMOTION -> 추천 코드 공유시 티켓을 공짜로 주는 프로모션
            CHARGED -> 결제로 인해 쌓이는 티켓
        sign (-)
            REFUND -> 티켓 환불
            USED_TICKET -> 티켓 사용

            USED_PROMOTION -> 티켓 사용
                amount = 0 처리
                프르모션 적용으로 티켓을 사용안할 때도 내역 쌓아야 함.
                -> ticket_usage_results.ticket_id update에 필요
    """

    SURVEY_PROMOTION = 0
    SHARE_PROMOTION = 1
    CHARGED = 2
    REFUND = 3
    USED_TICKET = 4
    USED_PROMOTION = 5


class RecommendCodeMaxCountEnum(Enum):
    """
        사용모델 : RecommendCodeModel
        추천코드 만료 사용 횟수
    """

    MAX_COUNT = 2
