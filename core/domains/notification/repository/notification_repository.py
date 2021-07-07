from datetime import timedelta
from typing import Optional, List

from app.extensions.utils.log_helper import logger_
from app.extensions.utils.time_helper import get_server_timestamp

from app.extensions.database import session
from app.persistence.model import NotificationModel, ReceivePushTypeHistoryModel
from app.persistence.model.receive_push_type_model import ReceivePushTypeModel
from core.domains.notification.dto.notification_dto import GetBadgeDto, GetNotificationDto, UpdateNotificationDto, \
    UpdateReceiveNotificationSettingDto
from core.domains.notification.entity.notification_entity import NotificationEntity, ReceivePushTypeEntity

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

    def get_receive_notification_settings(self, user_id: int) -> ReceivePushTypeEntity:
        filters = list()
        filters.append(ReceivePushTypeModel.user_id == user_id)

        receive_push_types = session.query(ReceivePushTypeModel).filter(*filters).first()
        return receive_push_types.to_entity()

    def update_receive_notification_setting(self, dto: UpdateReceiveNotificationSettingDto) -> None:
        try:
            filters = dict()
            filters["is_" + dto.push_type] = dto.is_active

            session.query(ReceivePushTypeModel).filter_by(user_id=dto.user_id).update(
                filters
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[NotificationRepository][update_receive_notification_settings] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def create_receive_push_type_history(self, dto: UpdateReceiveNotificationSettingDto) -> None:
        try:
            receive_push_type_history = ReceivePushTypeHistoryModel(
                user_id=dto.user_id,
                push_type=dto.push_type,
                is_active=dto.is_active
            )

            session.add(receive_push_type_history)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[NotificationRepository][create_receive_push_type_history] user_id : {dto.user_id} error : {e}"
            )
            raise Exception
