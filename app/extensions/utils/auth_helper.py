import requests
from flask import Response
from core.domains.authentication.enum.auth_enum import AuthenticationEnum


def set_renew_token(expired_token: str) -> Response:
    return requests.get(
        url=AuthenticationEnum.CAPTAIN_BASE_URL.value
        + AuthenticationEnum.TOKEN_REFRESH_END_POINT.value,
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Cache-Control": "no-cache",
            "Authorization": "Bearer " + expired_token,
        },
    )
