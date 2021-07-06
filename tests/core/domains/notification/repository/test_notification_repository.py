from core.domains.notification.dto.notification_dto import GetBadgeDto, GetNotificationDto, UpdateNotificationDto
from core.domains.notification.entity.notification_entity import NotificationEntity
from core.domains.notification.enum.notification_enum import NotificationTopicEnum, NotificationBadgeTypeEnum, \
    NotificationHistoryCategoryEnum
from core.domains.notification.repository.notification_repository import NotificationRepository


def test_get_notification_repo_when_my_category_history_then_two_result(create_users, create_notifications):
    topics = [NotificationTopicEnum.SUB_NEWS.value, NotificationTopicEnum.SUB_SCHEDULE.value]
    get_notification_dto = GetNotificationDto(
        user_id=create_users[0].id,
        category=NotificationHistoryCategoryEnum.MY.value,
        topics=topics
    )
    notifications = NotificationRepository().get_notifications(dto=get_notification_dto)

    assert len(notifications) == len(topics)
    assert isinstance(notifications, list)
    assert isinstance(notifications[0], NotificationEntity)
    assert notifications[0].topic == create_notifications[0].topic
    assert notifications[1].topic == create_notifications[1].topic


def test_get_notification_repo_when_official_category_history_then_one_result(create_users, create_notifications):
    topics = [NotificationTopicEnum.OFFICIAL.value]
    get_notification_dto = GetNotificationDto(
        user_id=create_users[0].id,
        category=NotificationHistoryCategoryEnum.OFFICIAL.value,
        topics=topics
    )
    notifications = NotificationRepository().get_notifications(dto=get_notification_dto)

    assert len(notifications) == len(topics)
    assert isinstance(notifications, list)
    assert isinstance(notifications[0], NotificationEntity)
    assert notifications[0].topic == create_notifications[2].topic


def test_get_notification_repo_when_my_category_history_then_none(create_users, create_notifications):
    topics = [NotificationTopicEnum.SUB_NEWS.value, NotificationTopicEnum.SUB_SCHEDULE.value]
    get_notification_dto = GetNotificationDto(
        user_id=create_users[1].id,
        category=NotificationHistoryCategoryEnum.MY.value,
        topics=topics
    )
    notifications = NotificationRepository().get_notifications(dto=get_notification_dto)

    assert notifications == []
