import pytest
import requests

from app.extensions.queue import SqsTypeEnum, SenderDto
from app.extensions.queue.sqs_sender import SqsMessageSender
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.user.enum.user_enum import UserSqsTypeEnum


@pytest.mark.skip(reason="실제 SQS 전송")
def test_send_sqs(sqs: SqsMessageSender):
    total = 0
    while True:
        msg = SenderDto(
            msg_type=UserSqsTypeEnum.SEND_USER_DATA_TO_LAKE.value,
            msg=dict(user_id=total),
            msg_created_at=get_server_timestamp().strftime("%Y/%m/%d, %H:%M:%S"),
        )

        sqs.send_message(
            queue_type=SqsTypeEnum.USER_DATA_SYNC_TO_LAKE, msg=msg, logging=True
        )
        total += 1
        if total == 10:
            break

    assert 1 == 1


@pytest.mark.skip(reason="실제 SQS Message 조회")
def test_receive_sqs(sqs: SqsMessageSender):
    total = 0
    try:
        for message in sqs.receive_after_delete(
            queue_type=SqsTypeEnum.USER_DATA_SYNC_TO_LAKE
        ):
            test = message
            if message["Body"]:
                #### 처리 로직 -> data push to data lake ####

                ##########################################
                print("[receive_after_delete] Target Message {0}", message["Body"])
                total += 1
    except Exception as e:
        print("SQS Fail : {}".format(e))
        send_slack_message(
            "Exception: {}".format(str(e)),
            "[FAIL]" + SqsTypeEnum.USER_DATA_SYNC_TO_LAKE.value,
        )

    dict_ = {
        "result": True,
        "total": total,
    }
    return dict_


def send_slack_message(message, title):
    channel = "#engineering-class"

    text = title + " -> " + message
    slack_token = "xoxb-1811487173312-2075478573287-JtTJbgy3fAboqlwkLeas9R1o"
    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer " + slack_token},
        data={"channel": channel, "text": text},
    )
