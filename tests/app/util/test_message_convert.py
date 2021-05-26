from app.extensions.utils.message_converter import MessageConverter
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.notification.dto.notification_dto import PushMessageDto
from core.domains.notification.enum.notification_enum import NotificationCategoryEnum, NotificationBadgeTypeEnum


def test_message_convert():
    data = dict(
        user_id=1,
        created_at=str(get_server_timestamp().replace(microsecond=0)),
    )
    message_dto = PushMessageDto(
        token="device-token",
        category=NotificationCategoryEnum.APT01.value,
        badge_type=NotificationBadgeTypeEnum.ALL.value,
        title="모집공고가 새로 등록 되었습니다.",
        body="판교봇들마을3단지 모집공고가 게시되었습니다.",
        data=data
    )

    result = MessageConverter.to_dict(message_dto)
    assert result["message"]["token"] == message_dto.token
    assert result["message"]["category"] == message_dto.category
    assert result["message"]["badge_type"] == message_dto.badge_type
    assert result["message"]["notification"]["title"] == message_dto.title
    assert result["message"]["notification"]["body"] == message_dto.body
    assert result["message"]["data"]["user_id"] == 1
