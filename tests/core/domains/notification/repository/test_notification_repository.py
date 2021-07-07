from app.persistence.model import ReceivePushTypeHistoryModel
from core.domains.notification.dto.notification_dto import GetBadgeDto, GetNotificationDto, UpdateNotificationDto, \
    UpdateReceiveNotificationSettingDto
from core.domains.notification.entity.notification_entity import NotificationEntity, ReceivePushTypeEntity
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


# def test_get_receive_notification_settings_then_success(create_users):
#     result = NotificationRepository().get_receive_notification_settings(user_id=create_users[0].id)
#
#     assert isinstance(result, ReceivePushTypeEntity)
#     assert result.is_official is True
#     assert result.is_private is True
#     assert result.is_marketing is True
#
#
# def test_update_receive_notification_settings_then_success(create_users):
#     dto = UpdateReceiveNotificationSettingDto(
#         user_id=create_users[0].id,
#         push_type="official",
#         is_active=False
#     )
#     NotificationRepository().update_receive_notification_setting(dto=dto)
#     result = NotificationRepository().get_receive_notification_settings(user_id=dto.user_id)
#
#     assert isinstance(result, ReceivePushTypeEntity)
#     assert result.is_official is False
#
#
# def test_create_receive_notification_history_when_change_push_status_then_success(session, create_users):
#     dto = UpdateReceiveNotificationSettingDto(
#         user_id=create_users[0].id,
#         push_type="official",
#         is_active=False
#     )
#     NotificationRepository().create_receive_push_type_history(dto=dto)
#     result = session.query(ReceivePushTypeHistoryModel).filter_by(user_id=dto.user_id).all()
#
#     assert len(result) == 1
#     assert result[0].push_type == dto.push_type
#     assert result[0].is_active is False
#
#     dto.is_active = True
#     NotificationRepository().create_receive_push_type_history(dto=dto)
#     result = session.query(ReceivePushTypeHistoryModel).filter_by(user_id=dto.user_id).all()
#
#     assert len(result) == 2
#     assert result[1].push_type == dto.push_type
#     assert result[1].is_active is True
