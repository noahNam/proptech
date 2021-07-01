from pydantic import BaseModel


class PushMessageDto(BaseModel):
    # token: str
    title: str
    content: str
    created_at: str
    badge_type: str
    data: dict
