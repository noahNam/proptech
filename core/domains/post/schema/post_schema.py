from datetime import datetime
from typing import List

from pydantic import BaseModel
from pydantic.types import StrictInt, StrictStr


class PostResponseBaseSchema(BaseModel):
    id: StrictInt
    title: StrictStr
    body: StrictStr
    is_deleted: bool
    read_count: StrictInt
    created_at: StrictStr
    updated_at: StrictStr


class GetPostListResponseSchema(BaseModel):
    posts: List[PostResponseBaseSchema]


class UpdatePostReadCountResponseSchema(BaseModel):
    result: StrictStr
