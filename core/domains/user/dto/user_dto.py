from typing import List

from pydantic import BaseModel


class GetUserDto(BaseModel):
    user_id: int = None


class CreateUserDto(BaseModel):
    id: int
    nickname: str
    email: str = None
    birthday: str = None
    gender: str
    is_active: bool
    is_out: bool
    profile_img_id: int = None
    region_ids: List[int] = []
    file: List = []


class CreateUserProfileImgDto(BaseModel):
    user_id: int
    uuid_: str = None
    file_name: str = None
    path: str = None
    extension: str = None
    object_name: str = None
    origin_file: List = []
