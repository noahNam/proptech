from pydantic import BaseModel


class GetUserDto(BaseModel):
    user_id: int = None


class CreateUserDto(BaseModel):
    user_id: int
    nickname: str
    email: str = None
    birthday: str = None
    gender: str
    is_active: bool
    is_out: bool
    profile_img_id: int = None
