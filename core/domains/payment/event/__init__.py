from flask import g
from pubsub import pub

from core.domains.payment.enum import PaymentTopicEnum
from core.domains.payment.repository.payment_repository import PaymentRepository


def create_join_ticket(user_id: int,):
    if not PaymentRepository().is_join_ticket(user_id=user_id):
        PaymentRepository().create_join_ticket(user_id=user_id)

    setattr(g, PaymentTopicEnum.CREATE_JOIN_TICKET, None)


def get_number_of_ticket(user_id: int,):
    number_of_ticket = PaymentRepository().get_number_of_ticket(user_id=user_id)

    setattr(g, PaymentTopicEnum.GET_NUMBER_OF_TICKET, number_of_ticket)


pub.subscribe(create_join_ticket, PaymentTopicEnum.CREATE_JOIN_TICKET)
pub.subscribe(get_number_of_ticket, PaymentTopicEnum.GET_NUMBER_OF_TICKET)
