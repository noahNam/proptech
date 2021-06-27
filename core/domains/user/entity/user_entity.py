from pydantic import BaseModel


class UserInfoCodeValueEntity(BaseModel):
    detail_code: list = []
    name: list = []


class UserInfoEntity(BaseModel):
    id: int
    user_profile_id: int
    code: int
    user_value: str = None
    code_values: UserInfoCodeValueEntity = None


class UserInfoEmptyEntity(BaseModel):
    user_profile_id: int = None
    code: int
    user_value: str = None
    code_values: UserInfoCodeValueEntity = None
