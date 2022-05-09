import os
from celery import Celery

from app import create_app
from app.commands.enum import TopicEnum


def make_celery(app):
    celery = Celery(
        "celery",
        backend=app.config['BACKEND_RESULT'],
        broker=app.config['REDIS_URL'],
        timezone=app.config['TIMEZONE'],
        enable_utc=app.config['CELERY_ENABLE_UTC'],
        include=['app.commands.tasks'],
    )

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app = application = create_app(os.environ.get("FLASK_CONFIG") or "default")

celery = make_celery(app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from app.commands import tasks

    sender.add_periodic_task(
        20.0,
        tasks.start_worker.s(topic=TopicEnum.SET_REDIS.value),
        name='set-redis',
    )

    tasks.start_worker.delay(topic=TopicEnum.SYNC_HOUSE_DATA.value)


# celery -A celery_app.celery flower --address=localhost --port=5555
# celery -A celery_app.celery worker -B --loglevel=info -P threads -c 3

# def celery_state(task_id):
#     task = AsyncResult(id=task_id, app=app)
#
#     return {'state': task.state, 'info': task.info}
#
#
# def celery_stop(task_id):
#   try:
#     AbortableAsyncResult(task_id).abort()
#     AsyncResult(id=task_id).revoke(terminate=True, signal="SIGKILL")
#     print("task kill")
#     return Response("success task kill")
#   except Exception:
#     return Response("fail task kill")