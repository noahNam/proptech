from pydantic import (
    BaseModel,
    ValidationError,
    StrictInt,
)

from app.extensions.utils.log_helper import logger_
from core.domains.report.dto.report_dto import GetExpectedCompetitionDto
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class GetExpectedCompetitionSchema(BaseModel):
    user_id: StrictInt
    house_id: StrictInt


class GetExpectedCompetitionRequestSchema:
    def __init__(self, user_id, house_id):
        self.user_id = int(user_id) if user_id else None
        self.house_id = int(house_id)

    def validate_request_and_make_dto(self):
        try:
            schema = GetExpectedCompetitionSchema(
                user_id=self.user_id, house_id=self.house_id
            ).dict()
            return GetExpectedCompetitionDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetExpectedCompetitionRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
