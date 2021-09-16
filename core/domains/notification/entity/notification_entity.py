from datetime import datetime

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
    created_at: datetime


class NotificationHistoryEntity(BaseModel):
    category: str
    created_date: str
    diff_min: str
    is_read: bool
    title: str
    content: str
    data: dict


class ReceivePushTypeEntity(BaseModel):
    id: int
    user_id: int
    is_official: bool
    is_private: bool
    is_marketing: bool
    updated_at: datetime


class NoticeTemplateEntity(BaseModel):
    id: int
    title: str
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
