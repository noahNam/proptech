from pydantic import BaseModel


class PaymentUserDto(BaseModel):
    user_id: int


class UseHouseTicketDto(BaseModel):
    user_id: int
    house_id: int
    auth_header: str


class UseUserTicketDto(BaseModel):
    user_id: int
    auth_header: str


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
