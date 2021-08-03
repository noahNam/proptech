import sentry_sdk

from flask import Blueprint
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import ExpiredSignatureError

from core.exceptions import InvalidRequestException, TokenValidationErrorException

api: Blueprint = Blueprint(name="api/tanos", import_name=__name__)

from .authentication.v1.auth_view import *  # noqa isort:skip
from .user.v1.user_view import *  # noqa isort:skip
from .notification.v1.notification_view import *  # noqa isort:skip
from .house.v1.house_view import *  # noqa isort:skip
from .post.v1.post_view import *  # noqa isort:skip
from .main import *  # noqa isort:skip
from .house.v1.house_view import *  # noqa isort:skip
from .payment.v1.payment_view import *  # noqa isort:skip


@api.errorhandler(Exception)
def handle_custom_type_exception(error):
    sentry_sdk.capture_exception(error)
    check_custom_err = getattr(error, "type_", None)
    if check_custom_err:
        return {"type": error.type_["type_"], "message": error.msg}, error.code
    elif isinstance(check_custom_err, dict):
        return {"type": error.code, "message": error.msg}, error.code
    else:
        return (
            {
                "type": HTTPStatus.INTERNAL_SERVER_ERROR,
                "message": "internal_server_error",
            },
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@api.errorhandler(InvalidRequestException)
def handle_invalid_request_exception(error):
    sentry_sdk.capture_exception(error)
    return (
        {"type": error.message[0]["loc"][0], "message": "invalid_request_error"},
        error.status_code,
    )


@api.errorhandler(NoAuthorizationError)
def handle_no_authorization_exception(error):
    sentry_sdk.capture_exception(error)
    return (
        {"type": HTTPStatus.UNAUTHORIZED, "message": "unauthorized_error"},
        HTTPStatus.UNAUTHORIZED,
    )


@api.errorhandler(ExpiredSignatureError)
def handle_signature_has_expired_exception(error):
    pass


@api.errorhandler(TokenValidationErrorException)
def handle_token_validation_exception(error):
    sentry_sdk.capture_exception(error)
    return (
        {"type": error.code, "message": error.msg},
        error.code,
    )
