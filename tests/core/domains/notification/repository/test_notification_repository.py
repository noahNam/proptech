from app import NotificationModel
from core.domains.notification.dto.notification_dto import GetBadgeDto, GetNotificationDto, UpdateNotificationDto
from core.domains.notification.entity.notification_entity import NotificationEntity
from core.domains.notification.enum.notification_enum import NotificationTopicEnum, NotificationBadgeTypeEnum
from core.domains.notification.repository.notification_repository import NotificationRepository
from tests.seeder.factory import NotificationFactory


def test_get_notification_repo_when_my_category_history_then_two_result(create_users, create_notifications):
    topics = [NotificationTopicEnum.SUB_NEWS.value, NotificationTopicEnum.SUB_SCHEDULE.value]
    get_notification_dto = GetNotificationDto(
        user_id=create_users[0].id,
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
        topics=topics
    )
    notifications = NotificationRepository().get_notifications(dto=get_notification_dto)

    assert notifications is None


def test_get_badge_repo_when_my_page_then_return_true(create_users, create_notifications):
    get_badge_dto = GetBadgeDto(
        user_id=create_users[0].id,
        badge_type=NotificationBadgeTypeEnum.ALL.value
    )

    result = NotificationRepository().get_badge(dto=get_badge_dto)

    assert isinstance(result, bool)


# def test_update_notification_when_read_notification_then_return_true(session, create_users, create_notifications):
#     update_notification_dto = UpdateNotificationDto(
#         user_id=create_users[0].id,
#         notification_id=create_notifications[0].id
#     )
#
#     NotificationRepository().update_notification_is_read(dto=update_notification_dto)
#     notification = session.query(NotificationModel).filter_by(id=create_notifications[0].id).first()
#     assert 1 == 1
#     assert notification.is_read is True
