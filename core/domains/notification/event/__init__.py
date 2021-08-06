from flask import g
from pubsub import pub

from core.domains.notification.dto.notification_dto import GetBadgeDto
from core.domains.notification.enum import NotificationTopicEnum
from core.domains.notification.repository.notification_repository import (
    NotificationRepository,
)


def get_badge(dto: GetBadgeDto):
    is_badge: bool = NotificationRepository().get_badge(dto=dto)
    setattr(g, NotificationTopicEnum.GET_BADGE, is_badge)


pub.subscribe(get_badge, NotificationTopicEnum.GET_BADGE)
