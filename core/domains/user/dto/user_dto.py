from typing import List

from pydantic import BaseModel


class GetUserDto(BaseModel):
    user_id: int = None


class CreateUserDto(BaseModel):
    user_id: int
    home_owner_type: int
    interested_house_type: int
    is_required_agree_terms: bool
    is_active: bool
    is_out: bool
    region_ids: List[int] = []
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
