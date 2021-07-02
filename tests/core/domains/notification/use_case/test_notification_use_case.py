from core.domains.notification.dto.notification_dto import GetNotificationDto, UpdateNotificationDto, GetBadgeDto
from core.domains.notification.entity.notification_entity import NotificationHistoryEntity
from core.domains.notification.enum.notification_enum import NotificationHistoryCategoryEnum, NotificationTopicEnum
from core.domains.notification.use_case.v1.notification_use_case import GetNotificationUseCase, \
    UpdateNotificationUseCase, GetBadgeUseCase
from core.use_case_output import UseCaseSuccessOutput


def test_get_notification_use_case_when_official_category_then_return_one_result(session, create_users,
                                                                                 create_notifications):
    get_notification_dto = GetNotificationDto(
        user_id=create_users[0].id, category=NotificationHistoryCategoryEnum.OFFICIAL.value
    )
    result = GetNotificationUseCase().execute(dto=get_notification_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value[0], NotificationHistoryEntity)
    assert len(result.value) == 1
    assert result.value[0].data['topic'] == NotificationTopicEnum.OFFICIAL.value


def test_get_notification_use_case_when_my_category_then_return_two_result(session, create_users, create_notifications):
    get_notification_dto = GetNotificationDto(
        user_id=create_users[0].id, category=NotificationHistoryCategoryEnum.MY.value
    )
    result = GetNotificationUseCase().execute(dto=get_notification_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value[0], NotificationHistoryEntity)
    assert len(result.value) == 2
    assert result.value[0].data['topic'] == NotificationTopicEnum.SUB_NEWS.value
    assert result.value[1].data['topic'] == NotificationTopicEnum.SUB_SCHEDULE.value


def test_update_notification_use_case_when_read_push_then_success(session, create_users, create_notifications):
    get_notification_dto = UpdateNotificationDto(
        user_id=create_users[0].id, notification_id=create_notifications[0].id
    )
    result1 = UpdateNotificationUseCase().execute(dto=get_notification_dto)

    get_notification_dto = GetNotificationDto(
        user_id=create_users[0].id, category=NotificationHistoryCategoryEnum.MY.value
    )
    result2 = GetNotificationUseCase().execute(dto=get_notification_dto)

    assert isinstance(result1, UseCaseSuccessOutput)
    assert isinstance(result2, UseCaseSuccessOutput)
    assert result1.type == "success"
    assert result2.value[0].is_read is True


def test_get_badge_use_case_then_true(session, create_users, create_notifications):
    get_notification_dto = UpdateNotificationDto(
        user_id=create_users[0].id, notification_id=create_notifications[0].id
    )
    result1 = UpdateNotificationUseCase().execute(dto=get_notification_dto)

    get_notification_dto = GetBadgeDto(
        user_id=create_users[0].id, category=NotificationHistoryCategoryEnum.MY.value
    )
    result2 = GetNotificationUseCase().execute(dto=get_notification_dto)

    assert isinstance(result1, UseCaseSuccessOutput)
    assert isinstance(result2, UseCaseSuccessOutput)
    assert result1.type == "success"
    assert result2.value[0].is_read is True


def test_get_badge_repo_when_my_page_then_return_true(create_users, create_notifications):
    get_badge_dto = GetBadgeDto(
        user_id=create_users[0].id,
    )

    result = GetBadgeUseCase().execute(dto=get_badge_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value is True


def test_get_badge_repo_when_my_page_then_return_false(create_users, create_notifications):
    for notification in create_notifications:
        get_notification_dto = UpdateNotificationDto(
            user_id=create_users[0].id, notification_id=notification.id
        )
        UpdateNotificationUseCase().execute(dto=get_notification_dto)

    get_badge_dto = GetBadgeDto(
        user_id=create_users[0].id,
    )

    result = GetBadgeUseCase().execute(dto=get_badge_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value is False
