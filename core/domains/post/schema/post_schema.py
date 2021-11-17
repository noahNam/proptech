from typing import List

from pydantic import BaseModel
from pydantic.types import StrictStr

from core.domains.post.entity.post_entity import PostEntity, PostImagePathEntity


class GetPostListResponseSchema(BaseModel):
    posts: List[PostEntity]


class UpdatePostReadCountResponseSchema(BaseModel):
    result: StrictStr


class GetPostImagePathListResponseSchema(BaseModel):
    posts: List[PostImagePathEntity]
