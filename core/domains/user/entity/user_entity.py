from pydantic import BaseModel


class UserEntity(BaseModel):
    id: int
    is_required_agree_terms: int
    is_active: int
    is_out: int


class UserInfoCodeValueEntity(BaseModel):
    detail_code: list = []
    name: list = []


class UserInfoEntity(BaseModel):
    id: int
    user_profile_id: int
    code: int
    user_value: str = None
    # code_values: UserInfoCodeValueEntity = None
    code_values: list = []


class UserInfoEmptyEntity(BaseModel):
    user_profile_id: int = None
    code: int
    user_value: str = None
    code_values: UserInfoCodeValueEntity = None
