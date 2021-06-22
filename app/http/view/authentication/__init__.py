from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.local import LocalProxy


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
