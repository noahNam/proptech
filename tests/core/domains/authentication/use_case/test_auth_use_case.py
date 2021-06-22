from http import HTTPStatus
from random import randint
from unittest.mock import patch

import pytest

from app.extensions.utils.enum.cache_enum import RedisKeyPrefix, RedisExpire
from app.persistence.model import DeviceModel
from core.domains.authentication.dto.sms_dto import (
    MobileAuthSendSmsDto,
    MobileAuthConfirmSmsDto,
)
from core.domains.authentication.use_case.v1.auth_use_case import (
    MobileAuthSendSmsUseCase,
    MobileAuthConfirmSmsUseCase,
)
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput


@pytest.mark.skip(reason="local redis 실행 안할경우 편의상 skip")
@patch("app.extensions.sens.sms.SmsClient.send_sms")
def test_send_sms_when_first_login_then_success(send_sms, sms, redis):
    dto = MobileAuthSendSmsDto(user_id=1, phone_number="01044744412")
    send_sms.return_value = dict(status_code=202)
    result = MobileAuthSendSmsUseCase().execute(dto=dto)

    key = f"{RedisKeyPrefix.MOBILE_AUTH.value}:{dto.phone_number}"

    assert result.type == "success"
    assert isinstance(result, UseCaseSuccessOutput)
    assert redis.is_exists(key) == 1


@pytest.mark.skip(reason="local redis 실행 안할경우 편의상 skip")
def test_confirm_sms_when_first_login_then_success(sms, redis, session, user_factory):
    user = user_factory.build_batch(size=1)
    session.add_all(user)
    session.commit()

    phone_number = "01044744412"
    auth_number = str(randint(1000, 10000))
    key = f"{RedisKeyPrefix.MOBILE_AUTH.value}:{phone_number}"

    redis.set(
        key=key, value=auth_number, ex=RedisExpire.MOBILE_AUTH_TIME.value,
    )

    dto = MobileAuthConfirmSmsDto(
        user_id=1, phone_number="01044744412", auth_number=auth_number
    )
    result = MobileAuthConfirmSmsUseCase().execute(dto=dto)

    device = session.query(DeviceModel).filter_by(user_id=user[0].id).first()

    assert device.phone_number == dto.phone_number
    assert device.is_auth is True
    assert result.type == "success"
    assert isinstance(result, UseCaseSuccessOutput)
    assert redis.is_exists(key) == 0


@pytest.mark.skip(reason="local redis 실행 안할경우 편의상 skip")
def test_confirm_sms_when_first_login_with_wrong_auth_number_then_failure(
    sms, redis, session, user_factory
):
    user = user_factory.build_batch(size=1)
    session.add_all(user)
    session.commit()

    phone_number = user[0].devices[0].phone_number
    auth_number = str(randint(1000, 10000))
    key = f"{RedisKeyPrefix.MOBILE_AUTH.value}:{phone_number}"

    redis.set(
        key=key, value=auth_number, ex=RedisExpire.MOBILE_AUTH_TIME.value,
    )

    dto = MobileAuthConfirmSmsDto(
        user_id=1, phone_number=phone_number, auth_number=12345
    )
    result = MobileAuthConfirmSmsUseCase().execute(dto=dto)

    device = session.query(DeviceModel).filter_by(user_id=user[0].id).first()

    assert device.phone_number == phone_number
    assert result.type == "success"
    assert isinstance(result, UseCaseSuccessOutput)
    assert redis.is_exists(key) == 0
