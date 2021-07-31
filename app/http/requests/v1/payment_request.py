from pydantic import (
    BaseModel,
    ValidationError,
    StrictInt,
)

from app.extensions.utils.log_helper import logger_
from core.domains.user.dto.user_dto import GetUserDto
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class GetTicketUsageResultSchema(BaseModel):
    user_id: StrictInt


class GetTicketUsageResultRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetTicketUsageResultSchema(user_id=self.user_id,).dict()
            return GetUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetTicketUsageResultRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
