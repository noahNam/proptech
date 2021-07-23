from datetime import datetime
from typing import List

from pydantic import BaseModel

from core.domains.house.entity.house_entity import InterestHouseEntity
from core.domains.notification.entity.notification_entity import ReceivePushTypeEntity


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


class DeviceTokenEntity(BaseModel):
    id: int
    device_id: int
    token: str


class DeviceEntity(BaseModel):
    id: int
    user_id: int
    uuid: str
    os: str
    is_active: bool
    is_auth: bool
    phone_number: str = None
    endpoint: str = ""
    created_at: datetime
    updated_at: datetime
    device_token: DeviceTokenEntity = None


class UserProfileEntity(BaseModel):
    id: int
    user_id: int
    nickname: str
    last_update_code: int
    created_at: datetime
    updated_at: datetime


class UserEntity(BaseModel):
    id: int
    is_required_agree_terms: bool
    join_date: str
    is_active: bool
    is_out: bool
    device: DeviceEntity
    user_profile: UserProfileEntity = None
    receive_push_type: ReceivePushTypeEntity
    interest_houses: List[InterestHouseEntity] = None


class PointTypeEntity(BaseModel):
    id: int
    name: str
    division: str


class PointEntity(BaseModel):
    id: int
    user_id: int
    type: int
    amount: int
    sign: str
    created_by: str
    created_at: datetime
    point_type: PointTypeEntity = None
