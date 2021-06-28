import pytest

from app.extensions.queue import SqsTypeEnum, SenderDto
from app.extensions.queue.sqs_sender import SqsMessageSender
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.user.enum.user_enum import UserSqsTypeEnum


@pytest.mark.skip(reason="실제 SQS 전송")
def test_send_sqs(sqs: SqsMessageSender):
    msg = SenderDto(
        msg_type=UserSqsTypeEnum.SEND_USER_DATA_TO_LAKE.value,
        msg=dict(user_id=1),
        msg_created_at=get_server_timestamp().strftime("%Y/%m/%d, %H:%M:%S"),
    )

    sqs.send_message(
        queue_type=SqsTypeEnum.USER_DATA_SYNC_TO_LAKE, msg=msg, logging=True
    )

    assert 1 == 1
