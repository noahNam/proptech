from pydantic import BaseModel, StrictStr


class AuthenticationResponseSchema(BaseModel):
    result: StrictStr
