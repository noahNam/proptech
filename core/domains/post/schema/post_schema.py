from datetime import datetime
from typing import List

from pydantic import BaseModel
from pydantic.types import StrictInt, StrictStr

from core.domains.post.entity.post_entity import PostEntity


class GetPostListResponseSchema(BaseModel):
    posts: List[PostEntity]


class UpdatePostReadCountResponseSchema(BaseModel):
    result: StrictStr
