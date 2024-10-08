from pydantic import BaseModel, StrictInt, StrictStr, ValidationError

from app.extensions.utils.log_helper import logger_
from core.domains.authentication.dto.sms_dto import (
    MobileAuthSendSmsDto,
    MobileAuthConfirmSmsDto,
)
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class MobileAuthSmsSendSchema(BaseModel):
    user_id: StrictInt
    phone_number: StrictStr = None


class MobileAuthSmsConfirmSchema(BaseModel):
    user_id: StrictInt
    phone_number: StrictStr = None
    auth_number: StrictStr = None


class MobileAuthSmsSendSchemeRequest:
    def __init__(
        self, user_id, phone_number=None,
    ):
        self.user_id = user_id
        self.phone_number = phone_number

    def validate_request_and_make_dto(self):
        try:
            schema = MobileAuthSmsSendSchema(
                user_id=self.user_id, phone_number=self.phone_number,
            ).dict()
            return MobileAuthSendSmsDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[MobileAuthSmsSendSchemeRequest][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class MobileAuthSmsConfirmSchemeRequest:
    def __init__(
        self, user_id, auth_number=None, phone_number=None,
    ):
        self.user_id = user_id
        self.auth_number = auth_number
        self.phone_number = phone_number

    def validate_request_and_make_dto(self):
        try:
            schema = MobileAuthSmsConfirmSchema(
                user_id=self.user_id,
                auth_number=self.auth_number,
                phone_number=self.phone_number,
            ).dict()
            return MobileAuthConfirmSmsDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[MobileAuthSmsConfirmSchemeRequest][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
