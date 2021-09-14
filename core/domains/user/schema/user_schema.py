from typing import List, Optional, Union

from pydantic import BaseModel, StrictStr, StrictInt, StrictBool

from core.domains.user.entity.user_entity import UserInfoResultEntity


class GetUserBaseSchema(BaseModel):
    is_required_agree_terms: StrictBool
    is_active: StrictBool
    is_out: StrictBool


class GetUserMainBaseSchema(BaseModel):
    survey_step: StrictInt
    tickets: StrictInt
    is_badge: StrictBool
    nickname: Optional[StrictStr]


class GetSurveysBaseSchema(BaseModel):
    code: StrictInt
    value: Union[StrictStr, List]


class GetUserProviderBaseSchema(BaseModel):
    provider: StrictStr
    email: Optional[StrictStr]


class GetUserProfileBaseSchema(BaseModel):
    nickname: StrictStr


class GetUserResponseSchema(BaseModel):
    user: GetUserBaseSchema


class CreateUserResponseSchema(BaseModel):
    result: StrictStr


class CreateAppAgreeTermsResponseSchema(BaseModel):
    result: StrictStr


class UpsertUserInfoResponseSchema(BaseModel):
    result: StrictStr


class GetUserInfoResponseSchema(BaseModel):
    surveys: List[UserInfoResultEntity]


class PatchUserOutResponseSchema(BaseModel):
    result: StrictStr


class GetUserMainResponseSchema(BaseModel):
    result: GetUserMainBaseSchema


class GetSurveysResponseSchema(BaseModel):
    user_infos: List[GetSurveysBaseSchema]


class GetUserProfileResponseSchema(BaseModel):
    user: GetUserProfileBaseSchema


class UpdateUserProfileResponseSchema(BaseModel):
    result: StrictStr


class GetUserProviderResponseSchema(BaseModel):
    result: GetUserProviderBaseSchema
