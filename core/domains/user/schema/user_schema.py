from pydantic import BaseModel, StrictStr, StrictInt

from core.domains.user.entity.user_entity import UserInfoCodeValueEntity


class GetUserBaseSchema(BaseModel):
    is_required_agree_terms: bool
    is_active: bool
    is_out: bool


class GetUserResponseSchema(BaseModel):
    user: GetUserBaseSchema


class CreateUserResponseSchema(BaseModel):
    result: StrictStr


class CreateAppAgreeTermsResponseSchema(BaseModel):
    result: StrictStr


class UpsertUserInfoResponseSchema(BaseModel):
    result: StrictStr


class GetUserInfoResponseSchema(BaseModel):
    result: list


class PatchUserOutResponseSchema(BaseModel):
    result: StrictStr
