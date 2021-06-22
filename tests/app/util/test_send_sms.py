import pytest

from app.extensions.utils.enum.ncp_enum import SmsMessageEnum
from core.domains.authentication.dto.sms_dto import SendSmsDto


@pytest.mark.skip(reason="실제 문자전송")
def test_send_sms(sms):
    """
    문자 전송 테스트 시 skip 제거 후 구동
    """
    send_sms_dto: SendSmsDto = sms.make_signature()

    # make message
    to_number = "01044744412"
    message = sms.convert_message(
        content=SmsMessageEnum.SMS_AUTH_MESSAGE.value, to_number=to_number
    )
    send_sms_dto.message = message

    # send sms
    response = sms.send_sms(send_sms_dto)

    assert response["status_code"] == 202
