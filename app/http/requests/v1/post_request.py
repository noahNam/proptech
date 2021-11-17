from typing import Optional

from pydantic import BaseModel, StrictInt, ValidationError, validator

from app.extensions.utils.log_helper import logger_
from core.domains.post.dto.post_dto import GetPostListDto, UpdatePostReadCountDto
from core.domains.post.enum.post_enum import (
    PostOnlyImageEnum,
    PostCategoryEnum,
    PostCategoryDetailEnum,
)
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class GetPostListSchema(BaseModel):
    post_category: int
    post_category_detail: int
    previous_post_id: int = None
    only_image: int = None

    @validator("only_image")
    def check_only_image(cls, only_image) -> int:
        if (
            only_image == PostOnlyImageEnum.YES.value
            or only_image == PostOnlyImageEnum.NO.value
            or not only_image
        ):
            return only_image
        else:
            raise ValidationError("Invalid only_image value")

    @validator("post_category")
    def check_post_category(cls, post_category) -> int:
        category_list = tuple([elm.value for elm in list(PostCategoryEnum)])

        if post_category not in category_list:
            raise ValidationError("Invalid post_category parameter")

        return post_category

    @validator("post_category_detail")
    def check_post_category_detail(cls, post_category_detail) -> int:
        category_detail_list = tuple(
            [elm.value for elm in list(PostCategoryDetailEnum)]
        )

        if post_category_detail not in category_detail_list:
            raise ValidationError("Invalid post_category_detail parameter")

        return post_category_detail


class UpdatePostReadCountSchema(BaseModel):
    post_id: int


class GetPostListRequestSchema:
    def __init__(
        self, post_category, post_category_detail, previous_post_id, only_image
    ):
        self.post_category = int(post_category)
        self.post_category_detail = int(post_category_detail)
        self.previous_post_id = previous_post_id
        self.only_image = int(only_image) if only_image else PostOnlyImageEnum.NO.value

    def validate_request_and_make_dto(self):
        try:
            schema = GetPostListSchema(
                post_category=self.post_category,
                post_category_detail=self.post_category_detail,
                previous_post_id=self.previous_post_id,
                only_image=self.only_image,
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
