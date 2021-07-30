from typing import List

from pydantic import BaseModel, StrictStr

from core.domains.user.entity.user_entity import (
    UserProfileEntity,
    UserInfoResultEntity,
)


class GetUserBaseSchema(BaseModel):
    is_required_agree_terms: bool
    is_active: bool
    is_out: bool


class GetUserMainBaseSchema(BaseModel):
    survey_step: int
    tickets: int
    is_badge: bool


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


class GetSurveyResultResponseSchema(BaseModel):
    result: UserProfileEntity
