import inject

from app.extensions.queue.sender import QueueMessageSender
from app.extensions.queue.sqs_sender import SqsMessageSender
from core.domains.house.repository.house_repository import HouseRepository
from core.domains.notification.repository.notification_repository import NotificationRepository
from core.domains.user.repository.user_repository import UserRepository


def bind(binder, app):
    binder.bind_to_provider(UserRepository, UserRepository)
    binder.bind_to_provider(HouseRepository, HouseRepository)
    binder.bind_to_provider(NotificationRepository, NotificationRepository)
    binder.bind_to_provider(QueueMessageSender, SqsMessageSender)


def init_provider(app):
    inject.clear_and_configure(lambda binder: bind(binder, app))
