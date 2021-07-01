from pydantic import BaseModel


class NotificationEntity(BaseModel):
    id: int
    user_id: int
    token: str
    endpoint: str
    topic: str
    badge_type: str
    message: dict
    is_read: bool
    is_pending: bool
    status: int


