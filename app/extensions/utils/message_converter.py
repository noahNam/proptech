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
                # "uuid": str(uuid.uuid4()),
                # "token": dto.token,
                "title": dto.title,
                "body": dto.content,
                "created_at": dto.created_at,
                "badge_type": dto.badge_type,
                "data": dto.data,
            }
        }
        return dict(
            default=str(uuid.uuid4()), GCM=json.dumps(content, ensure_ascii=False)
        )

    @staticmethod
    def get_message(message: str):
        return json.loads(message["GCM"])["data"]
