import os
from enum import Enum


class UserSqsTypeEnum(Enum):
    SEND_USER_DATA_TO_LAKE = "send_user_data_to_lake"


class UserProviderCallEnum(Enum):
    CAPTAIN_BASE_URL = os.environ.get("CAPTAIN_BASE_URL")
    CALL_END_POINT = "/api/captain/v1/users/provider"


class UserTicketTypeDivisionEnum(Enum):
    """
    ticket_types.division 테이블에서 사용
    """

    FREE = "free"
    CHARGED = "charged"
    REFUND = "refund"


class UserTicketSignEnum(Enum):
    """
    tickets.sign 테이블에서 사용
    """

    PLUS = "plus"
    MINUS = "minus"


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

    STEP_NO = 0
    STEP_ONE = 1
    STEP_TWO = 2
    STEP_COMPLETE = 3
