from typing import List

from pydantic import BaseModel


class GetUserDto(BaseModel):
    user_id: int = None


class CreateUserDto(BaseModel):
    user_id: int
    is_required_agree_terms: bool
    is_active: bool
    is_out: bool
    uuid: str
    os: str
    is_active_device: bool
    is_auth: bool
    token: str


class CreateUserProfileImgDto(BaseModel):
    user_id: int
    uuid_: str = None
    file_name: str = None
    path: str = None
    extension: str = None
    object_name: str = None
    origin_file: List = []


class CreateAppAgreeTermsDto(BaseModel):
    user_id: int
    private_user_info_yn: bool
    required_terms_yn: bool
    receipt_marketing_yn: bool


class UpsertUserInfoDto(BaseModel):
    user_id: int
    user_profile_id: int = None
    code: int
    value: str
