from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


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


class UserAnalysisFormatText(ExtendedEnum):
    """
        사용모델 : UserAnalysisCategory, UserAnalysisCategoryDetail
        유저 분석시 사용할 output text를 convert 한다.
    """

    NICKNAME = "nickname"
    SUB_POINT = "청약가점"
    SUB_ACCOUNT_TOTAL_AMT = "청약저축총금액"
    CHILD_NUM = "자녀수"


class RegionEnum(Enum):
    """
        사용모델 : TicketUsageResultModel
    """

    THE_AREA = "해당지역"
    OTHER_GYEONGGI = "기타경기"
    OTHER_REGION = "기타지역"
