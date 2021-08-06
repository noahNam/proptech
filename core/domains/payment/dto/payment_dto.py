from pydantic import BaseModel


class PaymentUserDto(BaseModel):
    user_id: int


class UseTicketDto(BaseModel):
    user_id: int
    house_id: int


class CreateTicketDto(BaseModel):
    user_id: int
    type: int
    amount: int
    sign: str
    created_by: str


class UpdateTicketUsageResultDto(BaseModel):
    user_id: int
    public_house_id: int
    ticket_id: int


class UseRecommendCodeDto(BaseModel):
    user_id: int
    code: str
