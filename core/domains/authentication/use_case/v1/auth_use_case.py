from http import HTTPStatus
from random import randint
from typing import Union

from app.extensions.utils.event_observer import send_message, get_event_object
from app.extensions.utils.enum.cache_enum import RedisKeyPrefix, RedisExpire
from app.extensions.utils.enum.ncp_enum import SmsMessageEnum
from core.domains.authentication.dto.sms_dto import MobileAuthSendSmsDto, SendSmsDto, MobileAuthConfirmSmsDto
from core.domains.user.enum import UserTopicEnum
from core.exceptions import RedisErrorException
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput
from app import sms, redis

from app.extensions.utils.log_helper import logger_

logger = logger_.getLogger(__name__)


class MobileAuthSendSmsUseCase:
    def __init__(self):
        self._sms = sms
        self._redis = redis

    def execute(self, dto: MobileAuthSendSmsDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not self._redis.is_available():
            return UseCaseFailureOutput(
                type=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Can not connect to Redis",
                code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        auth_number = self._make_auth_number()
        auth_message = SmsMessageEnum.SMS_AUTH_MESSAGE.value.format(auth_number)

        send_sms_dto: SendSmsDto = self._sms.make_signature()
        send_sms_dto.message = self._sms.convert_message(content=auth_message, to_number=dto.phone_number)

        result: dict = self._sms.send_sms(send_sms_dto)
        if result['status_code'] != 202:
            return UseCaseFailureOutput(
                type=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Can not send SMS to NCP",
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        # redis set
        key = f"{RedisKeyPrefix.MOBILE_AUTH.value}:{dto.phone_number}"
        try:
            redis.set(
                key=key,
                value=auth_number,
                ex=RedisExpire.MOBILE_AUTH_TIME.value,
            )
        except Exception as e:
            logger.error(
                f"[MobileAuthSendSmsUseCase][redis] error : {e}"
            )
            raise RedisErrorException

        return UseCaseSuccessOutput()

    def _make_auth_number(self):
        return randint(1000, 10000)


class MobileAuthConfirmSmsUseCase:
    def __init__(self):
        self._redis = redis

    def execute(self, dto: MobileAuthConfirmSmsDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not self._redis.is_available():
            return UseCaseFailureOutput(
                type=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Can not connect to Redis",
                code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        key = f"{RedisKeyPrefix.MOBILE_AUTH.value}:{dto.phone_number}"
        auth_number = None
        try:
            if redis.is_exists(key) == 1:
                redis_auth_number = redis.get_by_key(key)
                auth_number = str(redis_auth_number.decode('utf-8'))
        except Exception as e:
            logger.error(
                f"[MobileAuthConfirmSmsUseCase][redis] error : {e}"
            )
            raise RedisErrorException
        finally:
            redis.delete(key)

        if auth_number != dto.auth_number:
            # 인증 실패
            return UseCaseSuccessOutput(
                value="failure"
            )

        # 인증 성공
        # DB에 phone_number, is_auth update
        self._update_user_mobile_auth_info(dto=dto)

        return UseCaseSuccessOutput(value="success")

    def _update_user_mobile_auth_info(self, dto: MobileAuthConfirmSmsDto) -> None:
        send_message(topic_name=UserTopicEnum.UPDATE_USER_MOBILE_AUTH_INFO, dto=dto)

        return get_event_object(topic_name=UserTopicEnum.UPDATE_USER_MOBILE_AUTH_INFO)


class AuthenticationUseCase:
    def execute(self) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        return UseCaseSuccessOutput()
