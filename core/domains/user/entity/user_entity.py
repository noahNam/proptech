from datetime import datetime
from typing import List

from pydantic import BaseModel

from core.domains.house.entity.house_entity import InterestHouseEntity
from core.domains.notification.entity.notification_entity import ReceivePushTypeEntity
from core.domains.user.enum.user_enum import UserTicketSignEnum, UserSurveyStepEnum
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


class TicketTypeEntity(BaseModel):
    id: int
    division: str


class TicketEntity(BaseModel):
    id: int
    user_id: int
    type: int
    amount: int
    sign: str
    created_by: str
    created_at: datetime
    ticket_type: TicketTypeEntity = None


class UserEntity(BaseModel):
    id: int
    is_required_agree_terms: bool
    join_date: str
    is_active: bool
    is_out: bool
    number_ticket: int
    device: DeviceEntity
    user_profile: UserProfileEntity = None
    receive_push_type: ReceivePushTypeEntity
    interest_houses: List[InterestHouseEntity] = None
    tickets: List[TicketEntity] = None

    @property
    def total_amount(self) -> int:
        total_amount = 0
        if not self.tickets:
            return total_amount

        for ticket in self.tickets:
            if ticket.sign == UserTicketSignEnum.PLUS.value:
                total_amount += ticket.amount
            else:
                total_amount -= ticket.amount

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


class SurveyResultEntity(BaseModel):
    id = int
    user_id = int
    total_point = int
    detail_point_house = int
    detail_point_family = int
    detail_point_bank = int
    public_newly_married = int
    public_first_life = int
    public_multiple_children = int
    public_old_parent = int
    public_agency_recommend = int
    public_normal = int
    private_newly_married = int
    private_first_life = int
    private_multiple_children = int
    private_old_parent = int
    private_agency_recommend = int
    private_normal = int
    hope_town_phase_one = int
    hope_town_phase_two = int
    created_at = datetime
    updated_at = datetime


class TicketUsageResultDetailEntity(BaseModel):
    id: int
    ticket_usage_result_id: int
    house_type: str
    subscription_type: str
    rank: int


class TicketUsageResultEntity(BaseModel):
    id: int
    user_id: int
    house_id: int
    is_active: bool
    created_at: datetime
    ticket_usage_result_details: TicketUsageResultDetailEntity
