from pydantic import BaseModel


class ReportUserDto(BaseModel):
    user_id: int = None


class GetExpectedCompetitionDto(BaseModel):
    user_id: int
    house_id: int


class GetSaleInfoDto(BaseModel):
    user_id: int
    house_id: int


class GetRecentlySaleDto(BaseModel):
    user_id: int
    house_id: int
