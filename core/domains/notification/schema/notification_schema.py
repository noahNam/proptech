from pydantic import BaseModel, StrictStr


class GetNotificationResponseSchema(BaseModel):
    messages: list


class GetBadgeResponseSchema(BaseModel):
    result: bool


class UpdateNotificationResponseSchema(BaseModel):
    result: StrictStr
