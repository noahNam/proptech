from flask import g
from pubsub import pub

from core.domains.payment.enum import PaymentTopicEnum
from core.domains.payment.repository.payment_repository import PaymentRepository
from core.domains.user.dto.user_dto import CreateUserDto


def create_recommend_code(dto: CreateUserDto):
    # PaymentRepository().create_recommend_code(dto=dto)
    setattr(g, PaymentTopicEnum.CREATE_RECOMMEND_CODE, None)


pub.subscribe(create_recommend_code, PaymentTopicEnum.CREATE_RECOMMEND_CODE)
