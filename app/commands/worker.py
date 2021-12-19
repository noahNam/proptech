import click
from flask import current_app

from app.commands.enum import TopicEnum
from core.domains.house.use_case.v1.house_worker_use_case import (
    PreCalculateAverageUseCase,
    AddLegalCodeUseCase,
    PreCalculateAdministrativeDivisionUseCase,
    UpsertUploadPhotoUseCase,
    ReplacePublicToPrivateUseCase,
    CheckNotUploadedPhotoUseCase,
)
from core.domains.notification.use_case.v1.notification_worker_use_case import (
    PrePrcsNotificationUseCase,
    ConvertNoticePushMessageUseCase,
)


def get_worker(topic: str):
    if topic == TopicEnum.PRE_PRCS_INTEREST_HOUSE.value:
        return PrePrcsNotificationUseCase(topic=topic)
    elif topic == TopicEnum.CONVERT_NOTICE_PUSH_MESSAGE.value:
        return ConvertNoticePushMessageUseCase(topic=topic)
    elif topic == TopicEnum.PRE_CALCULATE_AVERAGE_HOUSE.value:
        return PreCalculateAverageUseCase(topic=topic)
    elif topic == TopicEnum.ADD_LEGAL_CODE_HOUSE.value:
        return AddLegalCodeUseCase(topic=topic)
    elif topic == TopicEnum.PRE_CALCULATE_AVERAGE_ADMINISTRATIVE.value:
        return PreCalculateAdministrativeDivisionUseCase(topic=topic)
    elif topic == TopicEnum.UPSERT_UPLOAD_PUBLIC_SALES_AND_DETAIL_IMAGE.value:
        return UpsertUploadPhotoUseCase(topic=topic)
    elif topic == TopicEnum.REPLACE_PUBLIC_TO_PRIVATE_SALES.value:
        return ReplacePublicToPrivateUseCase(topic=topic)
    elif topic == TopicEnum.CHECK_NOT_UPLOADED_PHOTOS.value:
        return CheckNotUploadedPhotoUseCase(topic=topic)


@current_app.cli.command("start-worker")
@click.argument("topic")
def start_worker(topic):
    us = get_worker(topic)
    us.execute()
