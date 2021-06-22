import os
from enum import Enum


class AuthenticationEnum(Enum):
    CAPTAIN_BASE_URL = os.environ.get("CAPTAIN_BASE_URL") or ""
    TOKEN_REFRESH_END_POINT = "/api/captain/v1/refresh"
