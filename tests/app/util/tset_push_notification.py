import json
import logging
import time

import boto3
import pytest
from botocore.exceptions import ClientError

from app.extensions.utils.message_converter import MessageConverter
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import NotificationModel
from core.domains.notification.dto.notification_dto import PushMessageDto
from core.domains.notification.enum.notification_enum import (
    NotificationCategoryEnum,
    NotificationBadgeTypeEnum,
)

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
    data={
        "user_id": 1,
        "created_at": str(get_server_timestamp().replace(microsecond=0)),
    },
)


@pytest.mark.skip(reason="삭제 예정:Hawkeye local_test.py로 대체될 예정")
def test_push_message_via_SNS(session):
    # make notification message
    message_dict = MessageConverter.to_dict(message_dto)

    # notification message insert
    notification = NotificationModel(
        user_id=1,
        token="user-token",
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

    # 엔드포인트에 연결할 임의의 사용자 데이터. Amazon SNS는 이 데이터를 사용하지 않습니다. 이 데이터는 UTF-8 형식이어야 하며 2KB 미만이어야 한다.
    sns = boto3.resource("sns")
    platform_application = sns.PlatformApplication(APPLICATION_ARN)

    try:
        platform_application_endpoint = platform_application.create_platform_endpoint(
            Token=user_device_token, CustomUserData="1"
        ).arn
    except ClientError as e:
        logger.exception("Could not create to platform application endpoint. %s", e)
        raise e

    message = json.dumps(result[0].data, ensure_ascii=False)

    # push message to topic
    topic = sns.Topic(TOPIC_ARN)
    topic.subscribe(Protocol="application", Endpoint=platform_application_endpoint)
    res = topic.publish(Message=message, MessageStructure="json")

    assert res.get("ResponseMetadata").get("HTTPStatusCode") == 200


@pytest.mark.skip(reason="삭제 예정:Hawkeye local_test.py로 대체될 예정")
def test_sns_get_count_application_endpoint():
    start_time = time.time()
    sns = boto3.client("sns")

    # First call does not need a NextToken
    resp = sns.list_endpoints_by_platform_application(
        PlatformApplicationArn=APPLICATION_ARN
    )
    count = len(resp["Endpoints"])
    enabled_count = 0
    try:
        while True:
            for endpoint in resp["Endpoints"]:
                if endpoint["Attributes"]["Enabled"] == "true":
                    enabled_count += 1

            # For the Last request, "NextToken" will not be included,
            # which will throw an exception. We use this to exit the loop.
            resp = sns.list_endpoints_by_platform_application(
                PlatformApplicationArn=APPLICATION_ARN, NextToken=ENDPOINT
            )
            count += len(resp["Endpoints"])
    except Exception as e:
        pass

    finally:
        print("Total Number of Endpoints counted: " + str(count))
        print("Total Number of Endpoints enabled: " + str(enabled_count))
        print(
            "Percentage of Endpoints enabled: "
            + str((enabled_count / count) * 100)
            + "%"
        )
        print("Query time: %s seconds" % (time.time() - start_time))


@pytest.mark.skip(reason="삭제 예정:Hawkeye local_test.py로 대체될 예정")
def test_sns_get_value_application_endpoint():
    sns = boto3.client("sns")

    # First call does not need a NextToken
    resp = sns.list_endpoints_by_platform_application(
        PlatformApplicationArn=APPLICATION_ARN
    )

    try:
        for endpoint in resp["Endpoints"]:
            if endpoint["Attributes"]["Enabled"] == "true":
                endpoint_arn = endpoint["EndpointArn"]
                token = endpoint["Attributes"]["Token"]
                custom_user_data = endpoint["Attributes"]["CustomUserData"]
    except Exception as e:
        pass

    finally:
        print("endpoint_arn : ", endpoint_arn)
        print("endpoint_arn : ", token)
        print("endpoint_arn : ", custom_user_data)
