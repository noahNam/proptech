from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from core.domains.house.entity.house_entity import InterestHouseEntity
from core.domains.notification.entity.notification_entity import ReceivePushTypeEntity
from core.domains.payment.entity.payment_entity import TicketEntity
from core.domains.payment.enum.payment_enum import TicketSignEnum
from core.domains.user.enum.user_enum import UserSurveyStepEnum
from core.domains.user.enum.user_info_enum import CodeStepEnum


class UserInfoCodeValueEntity(BaseModel):
    detail_code: list = []
    name: list = []


class UserInfoResultEntity(BaseModel):
    code: int
    code_values: Optional[UserInfoCodeValueEntity]
    user_value: Optional[str]


class UserInfoEntity(BaseModel):
    user_profile_id: Optional[int]
    code: int
    value: Optional[str]


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


class SurveyResultEntity(BaseModel):
    id = int
    user_id = int
    total_point: Optional[int]
    detail_point_house: Optional[int]
    detail_point_family: Optional[int]
    detail_point_bank: Optional[int]
    public_newly_married: Optional[int]
    public_first_life: Optional[int]
    public_multiple_children: Optional[int]
    public_old_parent: Optional[int]
    public_agency_recommend: Optional[int]
    public_normal: Optional[int]
    private_newly_married: Optional[int]
    private_first_life: Optional[int]
    private_multiple_children: Optional[int]
    private_old_parent: Optional[int]
    private_agency_recommend: Optional[int]
    private_normal: Optional[int]
    hope_town_phase_one: Optional[int]
    hope_town_phase_two: Optional[int]
    created_at = datetime
    updated_at = datetime


class UserProfileEntity(BaseModel):
    id: int
    user_id: int
    nickname: str
    last_update_code: int
    survey_step: Optional[int]
    created_at: datetime
    updated_at: datetime
    user_infos: List[UserInfoResultEntity] = []
    survey_result: Optional[SurveyResultEntity]


class UserEntity(BaseModel):
    id: int
    is_required_agree_terms: bool
    join_date: str
    is_active: bool
    is_out: bool
    number_ticket: int
    device: DeviceEntity
    user_profile: Optional[UserProfileEntity]
    receive_push_type: ReceivePushTypeEntity
    interest_houses: Optional[List[InterestHouseEntity]]
    tickets: Optional[List[TicketEntity]]

    @property
    def total_amount(self) -> int:
        total_amount = 0
        if not self.tickets:
            return total_amount

        for ticket in self.tickets:
            if ticket.is_active:
                if ticket.sign == TicketSignEnum.PLUS.value:
                    total_amount += ticket.amount
                else:
                    total_amount -= ticket.amount

        return 0 if total_amount < 0 else total_amount

    @property
    def survey_step(self) -> int:
        if not self.user_profile:
            return UserSurveyStepEnum.STEP_NO.value

        if self.user_profile.last_update_code == CodeStepEnum.COMPLETE_ONE.value:
            # 1단계 마지막 설문 완료 시 설문단계 = 2단계 진행중으로 내려줌
            return UserSurveyStepEnum.STEP_TWO.value

        if self.user_profile.last_update_code == CodeStepEnum.COMPLETE_TWO.value:
            # 2단계 마지막 설문 완료 시 설문단계 = 설문완료로 내려줌
            return UserSurveyStepEnum.STEP_COMPLETE.value

        if self.user_profile.last_update_code in CodeStepEnum.ONE.value:
            # 1단계 진행중
            return UserSurveyStepEnum.STEP_ONE.value
        elif self.user_profile.last_update_code in CodeStepEnum.TWO.value:
            # 2단계 진행중
            return UserSurveyStepEnum.STEP_TWO.value


class RecentlyViewEntity(BaseModel):
    id: int
    user_id: int
    house_id: int
    type: int
    created_at: datetime
