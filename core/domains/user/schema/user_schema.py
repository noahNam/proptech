from pydantic import BaseModel, StrictStr


class CreateUserResponseSchema(BaseModel):
    result: StrictStr
