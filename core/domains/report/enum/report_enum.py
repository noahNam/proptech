from enum import Enum


class SortCompetitionEnum(Enum):
    """
        사용모델 : PredictedCompetitionModel

        LIMIT_NUM: 경쟁률 중 몇개를 sort 해서 보여줄지를 나타내는 value
    """

    LIMIT_NUM = 3


class TicketUsageTypeEnum(Enum):
    """
        사용모델 : TicketUsageResultModel
    """

    HOUSE = "house"
    USER = "user"
    SUBS = "subs"
