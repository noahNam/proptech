from http import HTTPStatus
from typing import Union, Optional, List

import inject

from core.domains.notification.dto.notification_dto import GetNotificationDto
from core.domains.notification.entity.notification_entity import NotificationEntity
from core.domains.notification.repository.notification_repository import NotificationRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class NotificationBaseUseCase:
    @inject.autoparams()
    def __init__(self, notification_repo: NotificationRepository):
        self._notification_repo = notification_repo


class GetUserUseCase(NotificationBaseUseCase):
    def execute(self, dto: GetNotificationDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )


        notifications: List[NotificationEntity] = self._notification_repo.get_notifications(dto=dto)
        return UseCaseSuccessOutput()
