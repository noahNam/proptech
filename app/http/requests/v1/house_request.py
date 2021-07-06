from pydantic import BaseModel, StrictInt, ValidationError

from app.extensions.utils.log_helper import logger_
from core.domains.house.dto.house_dto import UpsertInterestHouseDto
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class UpsertInterestHouseSchema(BaseModel):
    user_id: StrictInt
    house_id: StrictInt
    type: StrictInt
    is_like: bool


class UpsertInterestHouseRequestSchema:
    def __init__(
            self, user_id, house_id, type_, is_like
    ):
        self.user_id = int(user_id) if user_id else None
        self.house_id = house_id
        self.type = type_
        self.is_like = is_like

    def validate_request_and_make_dto(self):
        try:
            schema = UpsertInterestHouseSchema(
                user_id=self.user_id,
                house_id=self.house_id,
                type=self.type,
                is_like=self.is_like,
            ).dict()
            return UpsertInterestHouseDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UpsertInterestHouseRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
