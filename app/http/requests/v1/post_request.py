from typing import Optional

from pydantic import BaseModel, StrictInt, ValidationError

from app.extensions.utils.log_helper import logger_
from core.domains.post.dto.post_dto import GetPostListDto, UpdatePostReadCountDto
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class GetPostListSchema(BaseModel):
    post_category: int
    post_category_detail: int


class UpdatePostReadCountSchema(BaseModel):
    post_id: int


class GetPostListRequestSchema:
    def __init__(self, post_category, post_category_detail):
        self.post_category = int(post_category)
        self.post_category_detail = int(post_category_detail)

    def validate_request_and_make_dto(self):
        try:
            schema = GetPostListSchema(
                post_category=self.post_category,
                post_category_detail=self.post_category_detail,
            ).dict()
            return GetPostListDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetPostListRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UpdatePostReadCountRequestSchema:
    def __init__(self, post_id):
        self.post_id = post_id

    def validate_request_and_make_dto(self):
        try:
            schema = UpdatePostReadCountSchema(post_id=self.post_id).dict()
            return UpdatePostReadCountDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UpdatePostReadCountRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
