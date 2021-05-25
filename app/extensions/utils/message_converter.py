import uuid
from app.extensions.utils.time_helper import get_server_timestamp

# from core.domains.notification.dto.notification_dto import MessageDto


class PushNoticeMessageConverter:
    """
    uuid: custom user data for AWS SNS service
    """

    @staticmethod
    def to_dict(dto: MessageDto):
        return {
            "message": {
                "uuid": str(uuid.uuid4()),
                "token": dto.token,
                "category": dto.category,
                "badge_type": dto.type,
                "notification": {
                    "title": dto.title,
                    "body": dto.body,
                },
                "data": {
                    # todo. 모집공고ID 필요 -> 현재 Schema가 없으므로 일단 Pass
                    "user_id": dto.user_id,
                    "created_at": str(get_server_timestamp().replace(microsecond=0)),
                },
            }
        }
