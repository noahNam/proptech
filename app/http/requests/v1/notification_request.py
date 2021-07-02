from pydantic import BaseModel, StrictInt, ValidationError

from app.extensions.utils.log_helper import logger_
from core.domains.notification.dto.notification_dto import GetNotificationDto, GetBadgeDto, UpdateNotificationDto
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class GetNotificationSchema(BaseModel):
    user_id: StrictInt
    category: str


class GetNotificationBadgeSchema(BaseModel):
    user_id: StrictInt
    badge_type: str = None


class UpdateNotificationSchema(BaseModel):
    user_id: StrictInt
    notification_id: StrictInt


class GetNotificationRequestSchema:
    def __init__(
            self, user_id, category
    ):
        self.user_id = int(user_id) if user_id else None
        self.category = category

    def validate_request_and_make_dto(self):
        try:
            schema = GetNotificationSchema(
                user_id=self.user_id,
                category=self.category,
            ).dict()
            return GetNotificationDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetNotificationRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetBadgeRequestSchema:
    def __init__(
            self, user_id, badge_type
    ):
        self.user_id = int(user_id) if user_id else None
        self.badge_type = badge_type

    def validate_request_and_make_dto(self):
        try:
            schema = GetNotificationBadgeSchema(
                user_id=self.user_id,
                badge_type=self.badge_type,
            ).dict()
            return GetBadgeDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetBadgeRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UpdateNotificationRequestSchema:
    def __init__(
            self, user_id, notification_id
    ):
        self.user_id = int(user_id) if user_id else None
        self.notification_id = notification_id

    def validate_request_and_make_dto(self):
        try:
            schema = UpdateNotificationSchema(
                user_id=self.user_id,
                notification_id=self.notification_id,
            ).dict()
            return UpdateNotificationDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UpdateNotificationRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
