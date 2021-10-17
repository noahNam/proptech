from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from core.domains.house.entity.house_entity import InterestHouseEntity
from core.domains.notification.entity.notification_entity import ReceivePushTypeEntity
from core.domains.payment.entity.payment_entity import TicketEntity
from core.domains.payment.enum.payment_enum import TicketSignEnum
from core.domains.report.entity.report_entity import SurveyResultEntity


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


class UserProfileEntity(BaseModel):
    id: int
    user_id: int
    nickname: str
    last_update_code: int
    survey_step: Optional[int]
    created_at: datetime
    updated_at: datetime
    user_infos: Optional[List[UserInfoResultEntity]]
    survey_results: Optional[List[SurveyResultEntity]]


class UserEntity(BaseModel):
    id: int
    email: Optional[str]
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


class PushTargetEntity(BaseModel):
    id: int
    is_active: bool
    device: DeviceEntity


class RecentlyViewEntity(BaseModel):
    id: int
    user_id: int
    house_id: int
    type: int
    created_at: datetime


class SidoCodeEntity(BaseModel):
    id: int
    sido_name: str
    sigugun_name: str
