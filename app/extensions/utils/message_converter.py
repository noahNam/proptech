import uuid

from core.domains.notification.dto.notification_dto import PushMessageDto


class MessageConverter:
    """
    uuid: custom user data for AWS SNS service
    """

    @classmethod
    def to_dict(cls, dto: PushMessageDto):
        return {
            "message": {
                "uuid": str(uuid.uuid4()),
                "token": dto.token,
                "category": dto.category,
                "badge_type": dto.badge_type,
                "notification": {
                    "title": dto.title,
                    "body": dto.body,
                },
                "data": dto.data,
            }
        }
