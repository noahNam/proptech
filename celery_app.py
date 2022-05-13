import os
from celery import Celery

from app import create_app
from app.commands.enum import TopicEnum


def make_celery(app):
    celery = Celery(
        "celery",
        backend=app.config["BACKEND_RESULT"],
        broker=app.config["REDIS_URL"],
        timezone=app.config["TIMEZONE"],
        enable_utc=app.config["CELERY_ENABLE_UTC"],
        include=["app.commands.tasks"],
    )

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


"""
    celery 실행명령어 -> celery -A celery_app.celery worker -B --loglevel=info -P threads -c 2
    flower 실행명령어 -> celery -A celery_app.celery flower --address=localhost --port=5555
"""
app = application = create_app(os.environ.get("FLASK_CONFIG") or "default")

celery = make_celery(app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from app.commands import tasks

    # set-redis 테스트용 task
    # sender.add_periodic_task(
    #     20.0,
    #     tasks.start_worker.s(topic=TopicEnum.SET_REDIS.value),
    #     name='set-redis',
    # )

    tasks.start_worker.delay(topic=TopicEnum.SYNC_HOUSE_DATA.value)
