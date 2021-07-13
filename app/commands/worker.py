import click
from flask import current_app

from app.commands.enum import TopicEnum
from core.domains.notification.use_case.v1.notification_worker_use_case import PrePrcsNotificationUseCase


def get_worker(topic: str):
    if topic == TopicEnum.PRE_PRCS_INTEREST_HOUSE.value:
        return PrePrcsNotificationUseCase(topic=topic)


@current_app.cli.command("start-worker")
@click.argument("topic")
def start_worker(topic):
    us = get_worker(topic)
    us.execute()


if __name__ == "__main__":
    start_worker(topic="tanos.pre_prcs_interest_house_data.v1")
