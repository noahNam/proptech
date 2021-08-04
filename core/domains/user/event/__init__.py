from flask import g
from pubsub import pub

from core.domains.notification.dto.notification_dto import (
    UpdateReceiveNotificationSettingDto,
)
from core.domains.user.dto.user_dto import CreateUserDto, RecentlyViewDto
from core.domains.user.enum import UserTopicEnum
from core.domains.user.repository.user_repository import UserRepository


def update_app_agree_terms_to_receive_marketing(
        dto: UpdateReceiveNotificationSettingDto,
):
    UserRepository().update_app_agree_terms_to_receive_marketing(dto=dto)
    setattr(g, UserTopicEnum.UPDATE_APP_AGREE_TERMS_TO_RECEIVE_MARKETING, None)


def create_recently_view(dto: RecentlyViewDto):
    UserRepository().create_recently_view(dto=dto)
    setattr(g, UserTopicEnum.CREATE_RECENTLY_VIEW, None)


pub.subscribe(
    update_app_agree_terms_to_receive_marketing,
    UserTopicEnum.UPDATE_APP_AGREE_TERMS_TO_RECEIVE_MARKETING,
)
pub.subscribe(create_recently_view, UserTopicEnum.CREATE_RECENTLY_VIEW)
