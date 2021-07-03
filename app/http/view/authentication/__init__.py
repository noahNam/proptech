from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import ExpiredSignatureError
from werkzeug.local import LocalProxy

from app.extensions.utils.auth_helper import set_renew_token


class User:
    def __init__(self, _id):
        self.id = int(_id) if _id else None


def _get_user_id():
    user_id = get_jwt_identity()

    return User(user_id)


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
            auth_header = request.headers.get("Authorization")
            bearer, _, token = auth_header.partition(" ")
            set_renew_token(token).json()
            raise ExpiredSignatureError

    return wrapper
