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


class TokenNotFoundError(Exception):
    code = HTTPStatus.FORBIDDEN
    msg = "token_not_found"
    pass


class NotFoundException(Exception):
    code = HTTPStatus.NOT_FOUND
    msg = "not_found"
    pass


class IsNotAdminException(Exception):
    code = HTTPStatus.FORBIDDEN
    msg = "is_not_admin"
    pass


class EmptyBodyException(Exception):
    code = HTTPStatus.BAD_REQUEST
    msg = "invalid_request"
    pass


class NoAuthorizationControlException(Exception):
    code = HTTPStatus.FORBIDDEN
    msg = "has_not_authorization_to_control"
    pass


class NotUniqueErrorException(Exception):
    code = HTTPStatus.BAD_REQUEST
    msg = "not_unique_error"
    pass