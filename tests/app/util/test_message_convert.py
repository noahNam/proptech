import json
import logging

import boto3
from botocore.exceptions import ClientError

from app.extensions.utils.message_converter import MessageConverter
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import NotificationModel
from core.domains.notification.dto.notification_dto import PushMessageDto
from core.domains.notification.enum.notification_enum import NotificationCategoryEnum, NotificationBadgeTypeEnum

logger = logging.getLogger(__name__)

TOPIC_ARN = "arn:aws:sns:ap-northeast-2:208389685150:test-notification-topic"
APPLICATION_ARN = "arn:aws:sns:ap-northeast-2:208389685150:app/GCM/test-app"
ENDPOINT = "cSKbASjPSAKH4zOu7eSJRb:APA91bED6HJa4snK8MWQ7Y90XTEtSV044Larhy-_rx0J0N4fqV3lTIHmzFYu_jV9xm7-MLQbSVtfYgHnJlQfKa_kgM4I9CK_3_a5IQMKYsPtXrJoXAsV8GmcCDr352bXMp6exgibcANc"

message_dto = PushMessageDto(
    token="device-token",
    category=NotificationCategoryEnum.APT01.value,
    badge_type=NotificationBadgeTypeEnum.ALL.value,
    title="모집공고가 새로 등록 되었습니다.",
    body="판교봇들마을3단지 모집공고가 게시되었습니다.",
    data={"user_id": 1, "created_at": str(get_server_timestamp().replace(microsecond=0))}
)


def test_push_message_via_SNS(
        session
):
    # make notification message
    message_dict = MessageConverter.to_dict(message_dto)

    # notification message insert
    notification = NotificationModel(
        user_id=1,
        endpoint=ENDPOINT,
        category="APT01",
        data=message_dict,
        is_read=False,
        is_pending=False,
    )
    session.add(notification)
    session.commit()

    # get notification message
    result = session.query(NotificationModel).filter_by(id=notification.id).all()

    # set user_device_token
    user_device_token = ENDPOINT

    # 엔드포인트에 연결할 임의의 사용자 데이터. Amazon SNS는 이 데이터를 사용하지 않습니다. 이 데이터는 UTF-8 형식이어야 하며 2KB 미만이어야 합니다.
    sns = boto3.resource('sns')
    platform_application = sns.PlatformApplication(APPLICATION_ARN)

    try:
        platform_application_endpoint = platform_application.create_platform_endpoint(
            Token=user_device_token,
            # CustomUserData=data1
        ).arn
    except ClientError as e:
        logger.exception("Could not create to platform application endpoint. %s", e)
        raise e

    message = json.dumps(result[0].data, ensure_ascii=False)

    # push message to topic
    topic = sns.Topic(TOPIC_ARN)
    topic.subscribe(Protocol='application', Endpoint=platform_application_endpoint)
    res = topic.publish(Message=message, MessageStructure='json')

    assert res.get("ResponseMetadata").get("HTTPStatusCode") == 200
