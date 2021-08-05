from pydantic import (
    BaseModel,
    ValidationError,
    StrictInt,
    StrictStr,
)

from app.extensions.utils.log_helper import logger_
from core.domains.payment.dto.payment_dto import (
    PaymentUserDto,
    UseTicketDto,
    UseRecommendCodeDto,
)
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class PaymentUserResultSchema(BaseModel):
    user_id: StrictInt


class UseBasicTicketSchema(BaseModel):
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
            schema = PaymentUserResultSchema(user_id=self.user_id,).dict()
            return PaymentUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetTicketUsageResultRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UseBasicTicketRequestSchema:
    def __init__(self, user_id, house_id):
        self.user_id = int(user_id) if user_id else None
        self.house_id = house_id

    def validate_request_and_make_dto(self):
        try:
            schema = UseBasicTicketSchema(
                user_id=self.user_id, house_id=self.house_id
            ).dict()
            return UseTicketDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UseTicketRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class CreateRecommendCodeRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = PaymentUserResultSchema(user_id=self.user_id,).dict()
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
            schema = PaymentUserResultSchema(user_id=self.user_id,).dict()
            return PaymentUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetRecommendCodeRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UseRecommendCodeRequestSchema:
    def __init__(self, user_id, code):
        self.user_id = int(user_id) if user_id else None
        self.code = code.lower()

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
