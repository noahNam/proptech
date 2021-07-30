from typing import Optional

from pydantic import BaseModel, StrictInt, ValidationError

from app.extensions.utils.log_helper import logger_
from core.domains.post.dto.post_dto import GetPostListDto, UpdatePostReadCountDto
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class GetPostListSchema(BaseModel):
    user_id: StrictInt
    post_category: int
    previous_post_id: Optional[int]


class UpdatePostReadCountSchema(BaseModel):
    user_id: StrictInt
    post_id: int


class GetPostListRequestSchema:
    def __init__(self, user_id, post_category, previous_post_id):
        self.user_id = int(user_id) if user_id else None
        self.post_category = int(post_category)
        self.previous_post_id = int(previous_post_id) if previous_post_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetPostListSchema(
                user_id=self.user_id,
                post_category=self.post_category,
                previous_post_id=self.previous_post_id,
            ).dict()
            return GetPostListDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetPostListRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UpdatePostReadCountRequestSchema:
    def __init__(self, user_id, post_id):
        self.user_id = int(user_id) if user_id else None
        self.post_id = post_id

    def validate_request_and_make_dto(self):
        try:
            schema = UpdatePostReadCountSchema(
                user_id=self.user_id, post_id=self.post_id,
            ).dict()
            return UpdatePostReadCountDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UpdatePostReadCountRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
