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


class GetUserInfoDto(BaseModel):
    user_id: int
    user_profile_id: int = None
    codes: list


class GetUserInfoDetailDto(BaseModel):
    user_id: int
    user_profile_id: int = None
    code: int


class SendUserInfoToLakeDto(BaseModel):
    user_id: int = None
    user_profile_id: int
    code: int
    value: str = None

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
