from pydantic import BaseModel, StrictStr, StrictInt

from core.domains.user.entity.user_entity import UserInfoCodeValueEntity


class GetUserInfoBaseSchema(BaseModel):
    code: StrictInt
    user_value: StrictStr = None
    code_values: UserInfoCodeValueEntity = None


class CreateUserResponseSchema(BaseModel):
    result: StrictStr


class CreateAppAgreeTermsResponseSchema(BaseModel):
    result: StrictStr


class UpsertUserInfoResponseSchema(BaseModel):
    result: StrictStr


class GetUserInfoResponseSchema(BaseModel):
    result: GetUserInfoBaseSchema
