import click
from flask import current_app

from app.commands.enum import TopicEnum
from core.domains.house.use_case.v1.house_worker_use_case import PreCalculateAverageUseCase
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


@current_app.cli.command("start-worker")
@click.argument("topic")
def start_worker(topic):
    us = get_worker(topic)
    us.execute()
