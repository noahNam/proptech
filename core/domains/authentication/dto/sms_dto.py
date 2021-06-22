from pydantic import BaseModel


class MobileAuthSendSmsDto(BaseModel):
    user_id: str = None
    phone_number: str = None


class MobileAuthConfirmSmsDto(BaseModel):
    user_id: str = None
    phone_number: str = None
    auth_number: str = None


class SendSmsDto(BaseModel):
    signing_key: str = None
    timestamp: str = None
    message: dict = None
