from app.commands.enum import TopicEnum
from celery_app import celery
from core.domains.house.use_case.v1.set_redis import SetRedisUseCase
from core.domains.house.use_case.v1.sync_data_to_mart import SyncDataUseCase


def get_task(topic: str):
    if topic == TopicEnum.SYNC_HOUSE_DATA.value:
        return SyncDataUseCase(topic=topic)
    elif topic == TopicEnum.SET_REDIS.value:
        return SetRedisUseCase()


@celery.task
def start_worker(topic):
    us = get_task(topic=topic)
    us.execute()