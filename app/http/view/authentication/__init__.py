from functools import wraps

from flask import request
from flask_jwt_extended.utils import decode_token

from app.http.view import api
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import ExpiredSignatureError
from werkzeug.local import LocalProxy
from core.exceptions import TokenValidationErrorException


class User:
    def __init__(self, _id: int, is_expired: bool):
        self.id = int(_id) if _id else None
        self.is_expired = is_expired


def _get_user_id():
    """
    - user_id = get_jwt_identity() 주석처리
        - jwt_required decorator 를 쓸 경우 expection이 나면 identity를 가져올 수 없는 문제가 있음.
        - 다른 validation 경우는 튕겨내면 되기 때문에 문제가 안되나, ExpiredSignatureError의 경우 요청을 모두 처리하고 토큰 갱신필요 여부를 응답 헤더에 내려줘야함.
        - 따라서 아래와 같이 ExpiredSignatureError의 경우 예외를 두어서 처리하도록 수정
    """
    auth_header = request.headers.get("Authorization")
    bearer, _, token = auth_header.partition(" ")
    is_expired = False
    decoded, user_id = None, None

    try:
        decoded = decode_token(token, allow_expired=False)
    except ExpiredSignatureError:
        decoded = decode_token(token, allow_expired=True)
        is_expired = True
    except Exception:
        pass

    if decoded:
        user_id = decoded['identity']

    return User(_id=user_id, is_expired=is_expired)


current_user = LocalProxy(_get_user_id)


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.id:
            raise NoAuthorizationError

        return fn(*args, **kwargs)

    return wrapper


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except ExpiredSignatureError:
            # 유효기간 만료 에러만 무시
            return fn(*args, **kwargs)
        except Exception:
            raise TokenValidationErrorException

    return wrapper


@api.after_request
def refresh_expiring_jwts(response):
    # Access Token이 만료되었을 때 응답헤더에 추가
    response.headers['Needs-Refresh-JWT'] = current_user.is_expired
    return response
