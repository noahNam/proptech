from datetime import timedelta
from typing import Optional, List

from sqlalchemy import literal, String
from sqlalchemy.orm import joinedload

from app.extensions.utils.log_helper import logger_
from app.extensions.utils.time_helper import get_server_timestamp

from app.extensions.database import session
from app.persistence.model import (
    NotificationModel,
    ReceivePushTypeHistoryModel,
    PublicSaleModel,
    InterestHouseModel,
    UserModel,
)
from app.persistence.model.notice_template_model import NoticeTemplateModel
from app.persistence.model.receive_push_type_model import ReceivePushTypeModel
from core.domains.house.entity.house_entity import PublicSalePushEntity
from core.domains.notification.dto.notification_dto import (
    GetBadgeDto,
    GetNotificationDto,
    UpdateNotificationDto,
    UpdateReceiveNotificationSettingDto,
)
from core.domains.notification.entity.notification_entity import (
    NotificationEntity,
    ReceivePushTypeEntity,
    NoticeTemplateEntity,
)
from core.domains.notification.enum.notification_enum import NotificationStatusEnum
from core.domains.user.entity.user_entity import PushTargetEntity

logger = logger_.getLogger(__name__)


class NotificationRepository:
    def get_notifications(
        self, dto: GetNotificationDto
    ) -> List[Optional[NotificationEntity]]:
        notification_filters = list()
        notification_filters.append(NotificationModel.user_id == dto.user_id)
        notification_filters.append(NotificationModel.status == NotificationStatusEnum.SUCCESS.value)
        notification_filters.append(
            NotificationModel.created_at >= get_server_timestamp() - timedelta(weeks=1)
        )
        notification_filters.append(NotificationModel.topic.in_(dto.topics))

        query = (
            session.using_bind("read_only")
            .query(NotificationModel)
            .filter(*notification_filters)
            .order_by(NotificationModel.created_at.desc())
        )

        notifications = query.all()
        if not notifications:
            return []

        return [notification.to_entity() for notification in notifications]

    def get_badge(self, dto: GetBadgeDto) -> bool:
        notification_filters = list()
        notification_filters.append(NotificationModel.user_id == dto.user_id)
        notification_filters.append(NotificationModel.is_read == False)
        notification_filters.append(NotificationModel.status == NotificationStatusEnum.SUCCESS.value)
        notification_filters.append(
            NotificationModel.created_at >= get_server_timestamp() - timedelta(weeks=1)
        )

        # MVP 단계에서는 제외
        # notification_filters.append(NotificationModel.badge_type == dto.badge_type)

        notifications = (
            session.using_bind("read_only")
            .query(NotificationModel)
            .filter(*notification_filters)
            .all()
        )

        # 읽지 않은 notification 이 있기 때문에 True 반환
        if notifications:
            return True

        return False

    def update_notification_is_read(self, dto: UpdateNotificationDto) -> None:
        try:
            session.query(NotificationModel).filter_by(id=dto.notification_id).update(
                {"is_read": True, "updated_at": get_server_timestamp()}
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

        receive_push_types = (
            session.query(ReceivePushTypeModel).filter(*filters).first()
        )
        return receive_push_types.to_entity()

    def update_receive_notification_setting(
        self, dto: UpdateReceiveNotificationSettingDto
    ) -> None:
        try:
            filters = dict()
            filters["is_" + dto.push_type] = dto.is_active
            filters["updated_at"] = get_server_timestamp()

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

    def create_receive_push_type_history(
        self, dto: UpdateReceiveNotificationSettingDto
    ) -> None:
        try:
            receive_push_type_history = ReceivePushTypeHistoryModel(
                user_id=dto.user_id, push_type=dto.push_type, is_active=dto.is_active,
            )

            session.add(receive_push_type_history)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[NotificationRepository][create_receive_push_type_history] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def get_push_target_of_public_sales(
        self, today: str
    ) -> List[Optional[PublicSalePushEntity]]:
        default_filters = list()
        default_filters.append(PublicSaleModel.is_available == True)

        # 모집공고일
        query_cond1 = (
            session.using_bind("read_only")
            .query(PublicSaleModel, literal("offer_date", String).label("message_type"))
            .filter(*default_filters, PublicSaleModel.offer_date == today)
        )

        # 특별공급일
        query_cond2 = (
            session.using_bind("read_only")
            .query(
                PublicSaleModel,
                literal("special_supply_date", String).label("message_type"),
            )
            .filter(*default_filters, PublicSaleModel.special_supply_date == today)
        )

        # 1순위
        query_cond3 = (
            session.using_bind("read_only")
            .query(
                PublicSaleModel,
                literal("first_supply_date", String).label("message_type"),
            )
            .filter(*default_filters, PublicSaleModel.first_supply_date == today)
        )

        # 2순위
        query_cond4 = (
            session.using_bind("read_only")
            .query(
                PublicSaleModel,
                literal("second_supply_date", String).label("message_type"),
            )
            .filter(*default_filters, PublicSaleModel.second_supply_date == today)
        )

        # 당첨자발표일
        query_cond5 = (
            session.using_bind("read_only")
            .query(
                PublicSaleModel,
                literal("notice_winner_date", String).label("message_type"),
            )
            .filter(*default_filters, PublicSaleModel.notice_winner_date == today)
        )

        query = query_cond1.union_all(
            query_cond2, query_cond3, query_cond4, query_cond5
        )
        public_sales = query.all()

        # public_sale[0] = PublicSaleModel
        # public_sale[1] = message_type
        return [
            public_sale[0].to_push_entity(public_sale[1])
            for public_sale in public_sales
        ]

    def get_users_of_private_push_target(
        self, house_id: int, type_: int
    ) -> List[PushTargetEntity]:
        filters = list()
        filters.append(InterestHouseModel.house_id == house_id)
        filters.append(InterestHouseModel.type == type_)
        filters.append(InterestHouseModel.is_like == True)

        query = (
            session.using_bind("read_only")
            .query(InterestHouseModel)
            .options(joinedload(InterestHouseModel.users, innerjoin=True))
            .options(joinedload("users.device", innerjoin=True))
            .options(joinedload("users.receive_push_type", innerjoin=True))
            .options(joinedload("users.device.device_token", innerjoin=True))
            .filter(*filters)
        )
        query_set = query.all()
        return self._make_private_push_target_user_list(query_set=query_set)

    def _make_private_push_target_user_list(
        self, query_set: List[InterestHouseModel]
    ) -> List[PushTargetEntity]:
        target_user_list = list()
        for query in query_set:
            if query.users.receive_push_type.is_private:
                target_user_list.append(query.users.to_push_target_entity())
        return target_user_list

    def create_notifications(self, notification_list: List[dict]) -> None:
        try:
            session.bulk_insert_mappings(
                NotificationModel, [notification for notification in notification_list]
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"[NotificationRepository][create_notifications] error : {e}")

    def get_notice_push_message(self) -> Optional[NoticeTemplateEntity]:
        query = (
            session.using_bind("read_only")
            .query(NoticeTemplateModel)
            .filter_by(is_active=True)
        )

        query_set = query.first()
        if not query_set:
            return None

        return query_set.to_entity()

    def get_users_of_notice_push_target(self) -> List[PushTargetEntity]:
        filters = list()
        filters.append(UserModel.is_active == True)

        query = (
            session.using_bind("read_only")
            .query(UserModel)
            .options(joinedload(UserModel.receive_push_type, innerjoin=True))
            .options(joinedload(UserModel.device, innerjoin=True))
            .options(joinedload("device.device_token", innerjoin=True))
            .filter(*filters)
        )
        query_set = query.all()
        return self._make_notice_push_target_user_list(query_set=query_set)

    def _make_notice_push_target_user_list(
        self, query_set: List[UserModel]
    ) -> List[PushTargetEntity]:
        target_user_list = list()
        for query in query_set:
            if query.receive_push_type.is_official:
                target_user_list.append(query.to_push_target_entity())
        return target_user_list

    def update_notice_templates_active(self) -> None:
        try:
            session.query(NoticeTemplateModel).filter_by(is_active=True).update(
                {"is_active": False, "updated_at": get_server_timestamp()}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[NotificationRepository][update_notice_templates_active] error : {e}"
            )
