import os
from enum import Enum


class UserSqsTypeEnum(Enum):
    SEND_USER_DATA_TO_LAKE = "send_user_data_to_lake"


class UserProviderCallEnum(Enum):
    CAPTAIN_BASE_URL = os.environ.get("CAPTAIN_BASE_URL")
    CALL_END_POINT = "/api/captain/v1/users/provider"
