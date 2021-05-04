from pydantic import BaseModel, StrictStr


class CreateUserResponseSchema(BaseModel):
    nickname: StrictStr
