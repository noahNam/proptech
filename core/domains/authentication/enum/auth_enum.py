from enum import Enum


class AuthenticationEnum(Enum):
    CAPTAIN_BASE_URL = "http://127.0.0.1:3000"
    # CAPTAIN_BASE_URL = "https://apartalk.com"
    TOKEN_REFRESH_END_POINT = "/api/captain/v1/refresh"
