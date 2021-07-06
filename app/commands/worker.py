import click
from flask import current_app

from app.commands.enum import TopicEnum
from core.domains.house.use_case.v1.house_use_case import PrePrcsInterestHouseUseCase


def get_worker(topic: str):
    if topic == TopicEnum.PRE_PRCS_INTEREST_HOUSE.value:
        return PrePrcsInterestHouseUseCase(topic=topic)


@current_app.cli.command("start-worker")
@click.argument("topic")
def start_worker(topic):
    us = get_worker(topic)
    us.execute()
