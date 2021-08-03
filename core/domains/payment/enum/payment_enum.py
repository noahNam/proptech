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
            JOIN_PROMOTION -> 회원가입 시 티켓을 공짜로 주는 프로모션
            CHARGED -> 결제로 인해 쌓이는 티켓
        sign (-)
            REFUND -> 티켓 환불
            USED_TICKET -> 티켓 사용

            USED_PROMOTION -> 티켓 사용
                amount = 0 처리
                프르모션 적용으로 티켓을 사용안할 때도 내역 쌓아야 함.
                -> ticket_usage_results.ticket_id update에 필요
    """

    JOIN_PROMOTION = 1
    CHARGED = 2
    REFUND = 3
    USED_TICKET = 4
    USED_PROMOTION = 5
