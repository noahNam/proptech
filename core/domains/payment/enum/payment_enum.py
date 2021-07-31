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
