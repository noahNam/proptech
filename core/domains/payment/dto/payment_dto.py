from pydantic import BaseModel


class PaymentUserDto(BaseModel):
    user_id: int = None
