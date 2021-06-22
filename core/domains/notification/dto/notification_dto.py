from pydantic import BaseModel


class PushMessageDto(BaseModel):
    token: str
    category: str
    badge_type: str
    title: str
    body: str
    data: dict
