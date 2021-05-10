from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.local import LocalProxy


def _get_user_id():
    user_id = get_jwt_identity()

    return int(user_id) if user_id else None


user_id = LocalProxy(_get_user_id)


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not user_id:
            raise NoAuthorizationError

        return fn(*args, **kwargs)

    return wrapper
