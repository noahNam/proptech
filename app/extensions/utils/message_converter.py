import json
import uuid

from core.domains.notification.dto.notification_dto import PushMessageDto


class MessageConverter:
    """
    AWS SNS message format
    - contain at least a top-level JSON key of "default" with a value that is a string.
    아래와 같이 하나의 content로 여러 type의 device에 메세지를 보낼 수 있다.
    {
      "default": "Content",
      "email": "Content",
      "GCM": "Content",
      "APNS": "Content"
    }
    """

    @staticmethod
    def to_dict(dto: PushMessageDto):
        content = {
            "data": {
                "created_at": dto.created_at,
                "badge_type": dto.badge_type,
                "data": dto.data,
            },
            "notification": {"title": dto.title, "body": dto.content,},
        }
        return dict(
            default=str(uuid.uuid4()), GCM=json.dumps(content, ensure_ascii=False)
        )

    @staticmethod
    def get_data(message: dict):
        return json.loads(message["GCM"])["data"]

    @staticmethod
    def get_notification_content(message: dict):
        return json.loads(message["GCM"])["notification"]
