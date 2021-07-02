from datetime import timedelta
from typing import Optional, List

from app import NotificationModel
from app.extensions.utils.log_helper import logger_
from app.extensions.utils.time_helper import get_server_timestamp

from app.extensions.database import session
from core.domains.notification.dto.notification_dto import GetBadgeDto, GetNotificationDto, UpdateNotificationDto
from core.domains.notification.entity.notification_entity import NotificationEntity

logger = logger_.getLogger(__name__)


class NotificationRepository:
    def get_notifications(self, dto: GetNotificationDto) -> List[Optional[NotificationEntity]]:
        notification_filters = list()
        notification_filters.append(NotificationModel.user_id == dto.user_id)
        notification_filters.append(NotificationModel.created_at >= get_server_timestamp() - timedelta(weeks=1))
        notification_filters.append(NotificationModel.topic.in_(dto.topics))

        notifications = session.query(NotificationModel).filter(*notification_filters).all()
        if not notifications:
            return []

        return [notification.to_entity() for notification in notifications]

    def get_badge(self, dto: GetBadgeDto) -> bool:
        notification_filters = list()
        notification_filters.append(NotificationModel.user_id == dto.user_id)
        notification_filters.append(NotificationModel.is_read == False)

        # MVP 단계에서는 제외
        # notification_filters.append(NotificationModel.badge_type == dto.badge_type)

        notifications = session.query(NotificationModel).filter(*notification_filters).all()

        # 읽지 않은 notification 이 있기 때문에 True 반환
        if notifications:
            return True

        return False

    def update_notification_is_read(self, dto: UpdateNotificationDto) -> None:
        try:
            session.query(NotificationModel).filter_by(
                id=dto.notification_id
            ).update(
                {"is_read": True}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[NotificationRepository][update_notification_is_read] notification_id : {dto.notification_id} error : {e}"
            )
