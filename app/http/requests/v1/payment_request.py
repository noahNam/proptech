from pydantic import (
    BaseModel,
    ValidationError,
    StrictInt,
    StrictStr,
)

from app.extensions.utils.log_helper import logger_
from core.domains.payment.dto.payment_dto import (
    PaymentUserDto,
    UseHouseTicketDto,
    UseRecommendCodeDto,
)
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class PaymentUserSchema(BaseModel):
    user_id: StrictInt


class UseHouseTicketSchema(BaseModel):
    user_id: StrictInt
    house_id: StrictInt


class UseRecommendCodeResultSchema(BaseModel):
    user_id: StrictInt
    code: StrictStr


class GetTicketUsageResultRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = PaymentUserSchema(user_id=self.user_id, ).dict()
            return PaymentUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetTicketUsageResultRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UseHouseTicketRequestSchema:
    def __init__(self, user_id, house_id):
        self.user_id = int(user_id) if user_id else None
        self.house_id = house_id

    def validate_request_and_make_dto(self):
        try:
            schema = UseHouseTicketSchema(
                user_id=self.user_id, house_id=self.house_id
            ).dict()
            return UseHouseTicketDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UseHouseTicketRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UseUserTicketRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = PaymentUserSchema(
                user_id=self.user_id
            ).dict()
            return PaymentUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UseUserTicketRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class CreateRecommendCodeRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = PaymentUserSchema(user_id=self.user_id, ).dict()
            return PaymentUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[CreateRecommendCodeRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetRecommendCodeRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = PaymentUserSchema(user_id=self.user_id, ).dict()
            return PaymentUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetRecommendCodeRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UseRecommendCodeRequestSchema:
    def __init__(self, user_id, code):
        self.user_id = int(user_id) if user_id else None
        self.code = code.upper()

    def validate_request_and_make_dto(self):
        try:
            schema = UseRecommendCodeResultSchema(
                user_id=self.user_id, code=self.code
            ).dict()
            return UseRecommendCodeDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UseRecommendCodeRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
