from pydantic import BaseModel


class GetExpectedCompetitionDto(BaseModel):
    user_id: int
    house_id: int
