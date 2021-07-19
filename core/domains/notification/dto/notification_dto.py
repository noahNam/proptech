from pydantic import BaseModel


class PushMessageDto(BaseModel):
    title: str
    content: str
    created_at: str
    badge_type: str
    data: dict


class GetNotificationDto(BaseModel):
    user_id: int
    category: str
    topics: list = []


class UpdateNotificationDto(BaseModel):
    user_id: int
    notification_id: int


class GetBadgeDto(BaseModel):
    user_id: int
    badge_type: str = None


class UpdateReceiveNotificationSettingDto(BaseModel):
    user_id: int
    push_type: str
    is_active: bool
