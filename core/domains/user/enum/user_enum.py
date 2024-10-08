import os
from enum import Enum


class UserSqsTypeEnum(Enum):
    SEND_USER_DATA_TO_LAKE = "send_user_data_to_lake"


class UserProviderCallEnum(Enum):
    CAPTAIN_BASE_URL = os.environ.get("CAPTAIN_BASE_URL")
    CALL_END_POINT = "/api/captain/v1/users/provider"


class UserTicketTypeDivisionEnum(Enum):
    """
    tickets.type 에서 사용
    """

    FREE = "free"
    CHARGED = "charged"
    REFUND = "refund"


class UserTicketCreatedByEnum(Enum):
    """
    tickets.created_by 테이블에서 사용
    """

    SYSTEM = "system"
    ADMIN = "admin"


class UserSurveyStepEnum(Enum):
    """
    유저 마이페이지 메인화면 호출 시 사용
    UserEntity 의 survey_step property
    """

    STEP_NO = 0  # 미진행
    STEP_ONE = 1  # 1단계 진행중
    STEP_TWO = 2  # 2단계 진행중
    STEP_COMPLETE = 3  # 완료
