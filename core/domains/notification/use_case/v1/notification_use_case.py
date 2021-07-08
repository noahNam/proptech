from http import HTTPStatus
from typing import Union, List

import inject

from app.extensions.utils.message_converter import MessageConverter
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.notification.dto.notification_dto import GetNotificationDto, UpdateNotificationDto, GetBadgeDto, \
    UpdateReceiveNotificationSettingDto
from core.domains.notification.entity.notification_entity import NotificationEntity, NotificationHistoryEntity, \
    ReceivePushTypeEntity
from core.domains.notification.enum.notification_enum import NotificationHistoryCategoryEnum, NotificationTopicEnum
from core.domains.notification.repository.notification_repository import NotificationRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class NotificationBaseUseCase:
    @inject.autoparams()
    def __init__(self, notification_repo: NotificationRepository):
        self._notification_repo = notification_repo


class GetNotificationUseCase(NotificationBaseUseCase):
    def execute(self, dto: GetNotificationDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )

        self._make_topics_object(dto=dto)
        notifications: List[NotificationEntity] = self._notification_repo.get_notifications(dto=dto)

        result: List[NotificationHistoryEntity] = self._make_history_entitiy(notifications=notifications, dto=dto)

        return UseCaseSuccessOutput(value=result)

    def _make_topics_object(self, dto: GetNotificationDto):
        topic_dict = {
            NotificationHistoryCategoryEnum.OFFICIAL.value: [NotificationTopicEnum.OFFICIAL.value],
            NotificationHistoryCategoryEnum.MY.value: [NotificationTopicEnum.SUB_NEWS.value,
                                                       NotificationTopicEnum.SUB_SCHEDULE.value]
        }

        topics = topic_dict.get(dto.category)
        dto.topics = topics

    def _make_history_entitiy(self, notifications: List[NotificationEntity], dto: GetNotificationDto) -> List[
        NotificationHistoryEntity]:
        result = list()

        for notification in notifications:
            created_date = notification.created_at.date().strftime("%Y%m%d")
            diff_min = str(
                round((get_server_timestamp() - notification.created_at).seconds / 60))

            message = MessageConverter.get_message(notification.message)

            notification_history_entity = NotificationHistoryEntity(
                category=dto.category,
                created_date=created_date,
                diff_min=diff_min,
                is_read=notification.is_read,
                title=message['title'],
                content=message['content'],
                data=dict(
                    id=notification.id,
                    user_id=notification.user_id,
                    topic=notification.topic
                )
            )
            result.append(notification_history_entity)

        return result


class UpdateNotificationUseCase(NotificationBaseUseCase):
    def execute(self, dto: UpdateNotificationDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )

        self._notification_repo.update_notification_is_read(dto=dto)
        return UseCaseSuccessOutput()


class GetBadgeUseCase(NotificationBaseUseCase):
    def execute(self, dto: GetBadgeDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )

        result: bool = self._notification_repo.get_badge(dto=dto)
        return UseCaseSuccessOutput(value=result)


class GetReceiveNotificationSettingUseCase(NotificationBaseUseCase):
    def execute(self, user_id: int) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )

        receive_push_types: ReceivePushTypeEntity = self._notification_repo.get_receive_notification_settings(
            user_id=user_id)
        result_dict = self._make_response_object(receive_push_types=receive_push_types)

        return UseCaseSuccessOutput(value=result_dict)

    def _make_response_object(self, receive_push_types: ReceivePushTypeEntity) -> dict:
        return dict(official=receive_push_types.is_official, private=receive_push_types.is_private,
                    marketing=receive_push_types.is_marketing)


class UpdateReceiveNotificationSettingUseCase(NotificationBaseUseCase):
    def execute(self, dto: UpdateReceiveNotificationSettingDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )

        self._notification_repo.update_receive_notification_setting(dto=dto)
        self._notification_repo.create_receive_push_type_history(dto=dto)

        return UseCaseSuccessOutput()
