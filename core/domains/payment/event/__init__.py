from flask import g
from pubsub import pub

from core.domains.payment.enum import PaymentTopicEnum
from core.domains.payment.repository.payment_repository import PaymentRepository


def create_join_ticket(user_id: int,):
    print("--> create_join_ticket start")
    test = PaymentRepository().is_join_ticket(user_id=user_id)
    print("--> test : ", test)
    if not PaymentRepository().is_join_ticket(user_id=user_id):
        PaymentRepository().create_join_ticket(user_id=user_id)

    setattr(g, PaymentTopicEnum.CREATE_JOIN_TICKET, None)


pub.subscribe(create_join_ticket, PaymentTopicEnum.CREATE_JOIN_TICKET)
