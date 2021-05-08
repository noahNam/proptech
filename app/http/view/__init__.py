from http import HTTPStatus

from flask import Blueprint
from flask_jwt_extended.exceptions import NoAuthorizationError

from core.exceptions import InvalidRequestException, NotUniqueErrorException

api: Blueprint = Blueprint(name="api/tanos", import_name=__name__)

from .authentication.v1.auth_view import *  # noqa isort:skip
from .user.v1.user_view import *  # noqa isort:skip


@api.errorhandler(Exception)
def handle_custom_type_exception(error):
    if bool(error.type_.get("type_")):
        return {'detail': error.type_["type_"], 'message': error.msg}, error.code
    else:
        return {'detail': error.code, 'message': error.msg}, error.code


@api.errorhandler(InvalidRequestException)
def handle_invalid_request_exception(error):
    return {"detail": error.message[0]["loc"][0], 'message': "invalid_request"}, error.status_code


@api.errorhandler(NoAuthorizationError)
def handle_no_authorization_exception(error):
    return {'detail': HTTPStatus.UNAUTHORIZED, 'message': "unauthorized_error"}, HTTPStatus.UNAUTHORIZED
