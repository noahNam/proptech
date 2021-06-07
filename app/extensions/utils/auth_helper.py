import requests
from flask import Response, jsonify
from flask_jwt_extended import decode_token
from jwt import InvalidTokenError

from core.domains.authentication.enum.auth_enum import AuthenticationEnum


def get_renew_token(expired_token: str) -> Response:
    try:
        decode_token(expired_token, allow_expired=True)
    except Exception:
        raise InvalidTokenError("Invalid Access_token")

    return requests.get(
        url=AuthenticationEnum.CAPTAIN_BASE_URL.value + AuthenticationEnum.TOKEN_REFRESH_END_POINT.value,
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Cache-Control": "no-cache",
            "Authorization": "Bearer " + expired_token
        }
    )
