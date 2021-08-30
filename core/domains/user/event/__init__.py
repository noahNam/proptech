from typing import Optional

from flask import g
from pubsub import pub

from core.domains.notification.dto.notification_dto import (
    UpdateReceiveNotificationSettingDto,
)
from core.domains.user.dto.user_dto import RecentlyViewDto, AvgMonthlyIncomeWokrerDto
from core.domains.user.entity.user_entity import UserProfileEntity, SidoCodeEntity
from core.domains.user.enum import UserTopicEnum
from core.domains.user.repository.user_repository import UserRepository


def get_user_survey_step(user_id: int):
    user_profile: Optional[UserProfileEntity] = UserRepository().get_user_profile(
        user_id=user_id
    )
    setattr(g, UserTopicEnum.GET_USER_SURVEY_STEP, user_profile)


def update_app_agree_terms_to_receive_marketing(
        dto: UpdateReceiveNotificationSettingDto,
):
    UserRepository().update_app_agree_terms_to_receive_marketing(dto=dto)
    setattr(g, UserTopicEnum.UPDATE_APP_AGREE_TERMS_TO_RECEIVE_MARKETING, None)


def create_recently_view(dto: RecentlyViewDto):
    UserRepository().create_recently_view(dto=dto)
    setattr(g, UserTopicEnum.CREATE_RECENTLY_VIEW, None)


def get_user_profile(user_id: int):
    result: Optional[UserProfileEntity] = UserRepository().get_user_profile(
        user_id=user_id
    )
    setattr(g, UserTopicEnum.GET_USER_PROFILE, result)


def get_sido_name(sido_id: int, sigugun_id: int):
    result: SidoCodeEntity = UserRepository().get_sido_name(
        sido_id=sido_id, sigugun_id=sigugun_id
    )
    setattr(g, UserTopicEnum.GET_SIDO_NAME, result)


def get_avg_monthly_income_workers():
    result: AvgMonthlyIncomeWokrerDto = UserRepository().get_avg_monthly_income_workers()
    setattr(g, UserTopicEnum.GET_AVG_MONTHLY_INCOME_WORKERS, result)


pub.subscribe(
    update_app_agree_terms_to_receive_marketing,
    UserTopicEnum.UPDATE_APP_AGREE_TERMS_TO_RECEIVE_MARKETING,
)
pub.subscribe(create_recently_view, UserTopicEnum.CREATE_RECENTLY_VIEW)
pub.subscribe(get_user_survey_step, UserTopicEnum.GET_USER_SURVEY_STEP)
pub.subscribe(get_user_profile, UserTopicEnum.GET_USER_PROFILE)
pub.subscribe(get_sido_name, UserTopicEnum.GET_SIDO_NAME)
pub.subscribe(get_avg_monthly_income_workers, UserTopicEnum.GET_AVG_MONTHLY_INCOME_WORKERS)
