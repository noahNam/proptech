from http import HTTPStatus


class InvalidRequestException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["detail"] = self.message
        return rv


class ErrorFormat(Exception):
    def __init__(self, **type_):
        self.type_ = type_


class NotFoundException(ErrorFormat):
    code = HTTPStatus.NOT_FOUND
    msg = "not_found_error"


class IsNotAdminException(ErrorFormat):
    code = HTTPStatus.FORBIDDEN
    msg = "is_not_admin"


class EmptyBodyException(ErrorFormat):
    code = HTTPStatus.BAD_REQUEST
    msg = "invalid_request_error"


class NoAuthorizationControlException(ErrorFormat):
    code = HTTPStatus.FORBIDDEN
    msg = "has_not_authorization_to_control"


class NotUniqueErrorException(ErrorFormat):
    code = HTTPStatus.BAD_REQUEST
    msg = "not_unique_error"


class IntegrityErrorException(ErrorFormat):
    code = HTTPStatus.BAD_REQUEST
    msg = "integrity_error"


class RedisErrorException(ErrorFormat):
    code = HTTPStatus.INTERNAL_SERVER_ERROR
    msg = "redis_error"


class TokenValidationErrorException(ErrorFormat):
    code = HTTPStatus.UNAUTHORIZED
    msg = "jwt_validation_error"


class UpdateFailErrorException(ErrorFormat):
    code = HTTPStatus.BAD_REQUEST
    msg = "update_fail_error"
