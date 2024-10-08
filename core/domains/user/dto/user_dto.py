from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class GetUserDto(BaseModel):
    user_id: int


class CreateUserDto(BaseModel):
    user_id: int
    email: Optional[str]
    phone_number: Optional[str]
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
    receive_marketing_yn: bool


class UpsertUserInfoDto(BaseModel):
    user_id: int
    user_profile_id: int = None
    codes: list
    values: list = []


class UpsertUserInfoDetailDto(BaseModel):
    user_id: int
    user_profile_id: int = None
    code: int
    value: str = None


class UpdateUserProfileDto(BaseModel):
    user_id: int
    nickname: str


class GetUserInfoDto(BaseModel):
    user_id: int
    user_profile_id: Optional[int]
    survey_step: int


class GetMonthlyIncomesDto(BaseModel):
    user_id: int
    is_married: str
    number_dependents: str


class SendUserInfoToLakeDto(BaseModel):
    user_id: Optional[int]
    user_profile_id: int
    code: int
    value: Optional[str]
    survey_step: Optional[int]

    def to_dict(self):
        return self.dict()


class AvgMonthlyIncomeWokrerDto(BaseModel):
    three: int
    four: int
    five: int
    six: int
    seven: int
    eight: int


class SidoCodeDto(BaseModel):
    sido_code: list
    sido_name: list


class SigugunCodeDto(BaseModel):
    sigugun_code: list
    sigugun_name: list


class RecentlyViewDto(BaseModel):
    user_id: int
    house_id: int
    type: int


class GetUserProviderDto(BaseModel):
    user_id: int
    auth_header: str


class UpdateFcmTokenDto(BaseModel):
    user_id: int
    fcm_token: str
