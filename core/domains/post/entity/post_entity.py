from datetime import datetime
from pydantic import BaseModel
from core.domains.user.entity.user_entity import UserEntity


class PostEntity(BaseModel):
    id: int
    user_id: int
    title: str
    body: str = None
    type: str
    is_deleted: bool
    read_count: int
    last_admin_action: str = None
    last_admin_action_at: datetime = None
    created_at: datetime
    updated_at: datetime
    user: UserEntity
    category_id: int
