from datetime import datetime
from typing import List

from pydantic import BaseModel


class PostAttachmentEntity(BaseModel):
    id: int
    post_id: int
    type: int
    file_name: str
    path: str
    extension: str
    created_at: datetime
    updated_at: datetime


class PostEntity(BaseModel):
    id: int
    category_id: int
    category_detail_id: int
    title: str
    body: str = None
    is_deleted: bool
    read_count: int
    post_attachments: List[PostAttachmentEntity] = None
    created_at: str
    updated_at: str
