from datetime import datetime
from typing import List

from pydantic import BaseModel

from core.domains.house.entity.house_entity import InterestHouseEntity
from core.domains.notification.entity.notification_entity import ReceivePushTypeEntity
from core.domains.user.enum.user_enum import UserPointSignEnum, UserSurveyStepEnum
from core.domains.user.enum.user_info_enum import CodeStepEnum


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
    points: List[PointEntity] = None

    @property
    def total_amount(self) -> int:
        total_amount = 0
        if not self.points:
            return total_amount

        for point in self.points:
            if point.sign == UserPointSignEnum.PLUS.value:
                total_amount += point.amount
            else:
                total_amount -= point.amount

        return 0 if total_amount < 0 else total_amount

    @property
    def survey_step(self) -> int:
        if not self.user_profile:
            return UserSurveyStepEnum.STEP_NO.value

        if self.user_profile.last_update_code in CodeStepEnum.ONE.value:
            return UserSurveyStepEnum.STEP_ONE.value
        elif self.user_profile.last_update_code in CodeStepEnum.TWO.value:
            return UserSurveyStepEnum.STEP_TWO.value
        else:
            return UserSurveyStepEnum.STEP_COMPLETE.value


class RecentlyViewEntity(BaseModel):
    id: int
    user_id: int
    house_id: int
    type: int
    created_at: datetime
