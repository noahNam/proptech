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
    code: int
    code_values: UserInfoCodeValueEntity = None
    user_value: str = None


class UserInfoEmptyEntity(BaseModel):
    code: int
    code_values: UserInfoCodeValueEntity = None
    user_value: str = None
