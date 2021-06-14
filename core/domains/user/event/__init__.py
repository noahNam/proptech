from flask import g
from pubsub import pub

from core.domains.user.dto.user_dto import CreateUserDto
from core.domains.user.enum import UserTopicEnum
from core.domains.user.repository.user_repository import UserRepository


def update_user_mobile_auth_info(dto: CreateUserDto):
    UserRepository().update_user_mobile_auth_info(dto=dto)
    setattr(g, UserTopicEnum.UPDATE_USER_MOBILE_AUTH_INFO, None)


pub.subscribe(update_user_mobile_auth_info, UserTopicEnum.UPDATE_USER_MOBILE_AUTH_INFO)
