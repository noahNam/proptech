import os
import sys
from time import time
from typing import List, Optional

import inject
import requests

from app.extensions.utils.log_helper import logger_
from app.extensions.utils.message_converter import MessageConverter
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.entity.house_entity import PublicSalePushEntity
from core.domains.house.enum.house_enum import HouseTypeEnum
from core.domains.notification.dto.notification_dto import PushMessageDto
from core.domains.notification.entity.notification_entity import NoticeTemplateEntity
from core.domains.notification.enum.notification_enum import (
    NotificationTopicEnum,
    NotificationBadgeTypeEnum,
    NotificationStatusEnum,
)
from core.domains.notification.repository.notification_repository import (
    NotificationRepository,
)
from core.domains.user.entity.user_entity import PushTargetEntity

logger = logger_.getLogger(__name__)


class BaseNotificationWorkerUseCase:
    @inject.autoparams()
    def __init__(self, topic: str, notification_repo: NotificationRepository):
        self._notification_repo = notification_repo
        self.topic = topic

    @property
    def client_id(self) -> str:
        return f"{self.topic}-{os.getpid()}"

    def send_slack_message(self, title: str, message: str):
        channel = "#batch-log"

        text = title + "\n" + message
        slack_token = os.environ.get("SLACK_TOKEN")
        if slack_token:
            requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer " + slack_token},
                data={"channel": channel, "text": text},
            )


class PrePrcsNotificationUseCase(BaseNotificationWorkerUseCase):
    def execute(self):
        start_time = time()
        logger.info(f"🚀\tPrePrcsNotification Start - {self.client_id}")

        # public sales 테이블의 모집공고일, 특별공급/1순위/2순위/당첨자발표일을 오늘 날짜 기준으로 조회한다.
        today = get_server_timestamp().strftime("%Y%m%d")
        try:
            target_public_sales: List[
                PublicSalePushEntity
            ] = self._notification_repo.get_push_target_of_public_sales(today=today)
            logger.info(
                f"🚀\tget_push_target_of_public_sales length - {len(target_public_sales)}"
            )
        except Exception as e:
            logger.error(f"🚀\tget_push_target_of_public_sales Error - {e}")
            self.send_slack_message(
                title="☠️ [PrePrcsNotificationUseCase] >>> 유저가 찜한 분양정보 중에 특별한 이벤트가 있을 경우 Push 보낼 메세지 Convert",
                message=f"get_push_target_of_public_sales Error - {e}",
            )
            sys.exit(0)

        try:
            if not target_public_sales:
                logger.info(
                    f"🚀\tPrePrcsNotification Success - nothing target_public_sales"
                )
                self.send_slack_message(
                    title="🚀 [PrePrcsNotificationUseCase] >>> 유저가 찜한 분양정보 중에 특별한 이벤트가 있을 경우 Push 보낼 메세지 Convert",
                    message=f"PrePrcsNotification Success - nothing target_public_sales!! \n "
                    f"records: {time() - start_time} secs",
                )
                sys.exit(0)

            notification_list: List[dict] = self._convert_message_for_public_sales(
                target_public_sales=target_public_sales
            )
        except Exception as e:
            logger.error(f"🚀\t_convert_message_for_public_sales Error - {e}")
            self.send_slack_message(
                title="☠️ [PrePrcsNotificationUseCase] >>> 유저가 찜한 분양정보 중에 특별한 이벤트가 있을 경우 Push 보낼 메세지 Convert",
                message=f"_convert_message_for_public_sales Error - {e}",
            )
            sys.exit(0)

        # notifications 테이블에 insert 한다.
        try:
            if not notification_list:
                logger.info(
                    f"🚀\tPrePrcsNotification Success - nothing notification_list"
                )
                self.send_slack_message(
                    title="🚀 [PrePrcsNotificationUseCase] >>> 유저가 찜한 분양정보 중에 특별한 이벤트가 있을 경우 Push 보낼 메세지 Convert",
                    message=f"PrePrcsNotification Success - nothing notification_list!! \n "
                    f"records: {time() - start_time} secs",
                )
                sys.exit(0)

            self._notification_repo.create_notifications(
                notification_list=notification_list
            )
        except Exception as e:
            logger.error(f"🚀\tcreate_private_notifications Error - {e}")
            self.send_slack_message(
                title="☠️ [PrePrcsNotificationUseCase] >>> 유저가 찜한 분양정보 중에 특별한 이벤트가 있을 경우 Push 보낼 메세지 Convert",
                message=f"create_private_notifications Error - {e}",
            )
            sys.exit(0)

        logger.info(
            f"🚀\tPrePrcsNotification Success -  {len(target_public_sales)} / {len(notification_list)}"
        )
        self.send_slack_message(
            title="🚀 [PrePrcsNotificationUseCase] >>> 유저가 찜한 분양정보 중에 특별한 이벤트가 있을 경우 Push 보낼 메세지 Convert",
            message=f"PrePrcsNotification Success -  {len(target_public_sales)} / {len(notification_list)} \n "
            f"records: {time() - start_time} secs",
        )

    def _convert_message_for_public_sales(
        self, target_public_sales: List[PublicSalePushEntity]
    ) -> List[dict]:
        notification_list = list()
        for target_public_sale in target_public_sales:
            """
            관심지역 새로운 분양매물 입주자공고, 당첨자발표 당일 알림 
            (분양소식) 관심 설정하신 00지역의 00분양의 입주자 공고가 등록되었습니다.
            -> SUB_NEWS = "apt002"

            관심매물 공고당일 알람 (특별공급, 1순위, 2순위 등) = 
            (분양일정) 관심 설정하신 000아파트의 특별공급 신청일입니다. 
            -> SUB_SCHEDULE = "apt003"
            """
            message_format_dict = dict(
                offer_date=[
                    "관심 설정하신 {0}지역 {1}의 입주자 공고가 등록되었습니다.",
                    "입주자공고 알림",
                    NotificationTopicEnum.SUB_NEWS.value,
                ],
                special_supply_date=[
                    "관심 설정하신 {1}의 특별공급 신청일 입니다.",
                    "특별공급 신청 알림",
                    NotificationTopicEnum.SUB_SCHEDULE.value,
                ],
                first_supply_date=[
                    "관심 설정하신 {1}의 1순위 신청일 입니다.",
                    "1순위 신청 알림",
                    NotificationTopicEnum.SUB_SCHEDULE.value,
                ],
                second_supply_date=[
                    "관심 설정하신 {1}의 2순위 신청일 입니다.",
                    "2순위 신청 알림",
                    NotificationTopicEnum.SUB_SCHEDULE.value,
                ],
                notice_winner_date=[
                    "관심 설정하신 {1}의 당첨자 발표일 입니다.",
                    "당첨자발표 알림",
                    NotificationTopicEnum.SUB_NEWS.value,
                ],
            )

            content = message_format_dict.get(target_public_sale.message_type)[
                0
            ].format(target_public_sale.region, target_public_sale.name)
            title = message_format_dict.get(target_public_sale.message_type)[1]
            topic = message_format_dict.get(target_public_sale.message_type)[2]

            # Push 타겟을 찜한 유저를 조회
            target_user_list: List[
                PushTargetEntity
            ] = self._notification_repo.get_users_of_private_push_target(
                house_id=target_public_sale.id, type_=HouseTypeEnum.PUBLIC_SALES.value
            )

            for target_user in target_user_list:
                if not target_user.is_active:
                    continue

                message_dto = PushMessageDto(
                    title=title,
                    content=content,
                    created_at=str(get_server_timestamp().replace(microsecond=0)),
                    badge_type=NotificationBadgeTypeEnum.ALL.value,
                    data={
                        # "user_id": target_user.id,
                        "topic": topic,
                    },
                )

                """
                    is_pending 
                    True  -> apt002, apt003 <매일아침 9시에 Lambda 발송>
                          -> apt001, apt004 <메뉴얼 람다 실행으로 발송>      
                    False -> 아직 해당 사항 없음 (실시간 푸쉬 발송)
                """
                is_pending = True
                message_dict = MessageConverter.to_dict(message_dto)
                notification_dict = dict(
                    user_id=target_user.id,
                    token=target_user.device.device_token.token,
                    endpoint=target_user.device.endpoint,
                    uuid=target_user.device.uuid,
                    topic=topic,
                    badge_type=NotificationBadgeTypeEnum.ALL.value,
                    message=message_dict,
                    is_read=False,
                    is_pending=is_pending,
                    status=NotificationStatusEnum.WAIT.value,
                )

                notification_list.append(notification_dict)

        return notification_list


class ConvertNoticePushMessageUseCase(BaseNotificationWorkerUseCase):
    def execute(self):
        start_time = time()
        logger.info(f"🚀\tConvertNoticePushMessage Start - {self.client_id}")
        notice_push_message, notification_list = None, None

        try:
            notice_push_message: Optional[
                NoticeTemplateEntity
            ] = self._notification_repo.get_notice_push_message()

        except Exception as e:
            logger.error(f"🚀\tget_notice_push_message Error - {e}")
            self.send_slack_message(
                title="☠️ [ConvertNoticePushMessageUseCase] >>> 공지사항 Push 보낼 메세지를 Convert",
                message=f"get_notice_push_message Error - {e}",
            )
            sys.exit(0)

        try:
            if notice_push_message:
                notification_list: List[dict] = self._convert_message_for_notice(
                    notice_push_message=notice_push_message
                )
                logger.info(f"🚀\tget_notice_push_message - {notice_push_message.title}")
            else:
                logger.info(f"🚀\t get_notice_push_message - nothing")

        except Exception as e:
            logger.error(f"🚀\t_convert_message_for_notice Error - {e}")
            self.send_slack_message(
                title="☠️ [ConvertNoticePushMessageUseCase] >>> 공지사항 Push 보낼 메세지를 Convert",
                message=f"_convert_message_for_notice Error - {e}",
            )
            sys.exit(0)

        # notifications 테이블에 insert 하고, notice_template 상태를 업데이트 한다.
        try:
            if notification_list:
                self._notification_repo.create_notifications(
                    notification_list=notification_list
                )

                self._notification_repo.update_notice_templates_active()
                logger.info(
                    f"🚀\tConvertNoticePushMessage Success - {len(notification_list)}"
                )
            else:
                logger.info(
                    f"🚀\tConvertNoticePushMessage Success - nothing notification_list"
                )

        except Exception as e:
            logger.error(f"🚀\tcreate_notice_notifications Error - {e}")
            self.send_slack_message(
                title="☠️ [ConvertNoticePushMessageUseCase] >>> 공지사항 Push 보낼 메세지를 Convert",
                message=f"create_notice_notifications Error - {e}",
            )
            sys.exit(0)

        self.send_slack_message(
            title="🚀 [ConvertNoticePushMessageUseCase] >>> 공지사항 Push 보낼 메세지를 Convert",
            message=f"ConvertNoticePushMessageUseCase Success - {len(notification_list)} \n "
            f"records: {time() - start_time} secs",
        )

        exit(os.EX_OK)

    def _convert_message_for_notice(
        self, notice_push_message: NoticeTemplateEntity
    ) -> List[dict]:
        notification_list = list()

        content = notice_push_message.content
        title = notice_push_message.content
        topic = NotificationTopicEnum.OFFICIAL.value

        # Push 타겟을 찜한 유저를 조회
        target_user_list: List[
            PushTargetEntity
        ] = self._notification_repo.get_users_of_notice_push_target()

        for target_user in target_user_list:
            if not target_user.is_active:
                continue

            message_dto = PushMessageDto(
                title=title,
                content=content,
                created_at=str(get_server_timestamp().replace(microsecond=0)),
                badge_type=NotificationBadgeTypeEnum.ALL.value,
                data={"topic": topic,},
            )

            """
                is_pending 
                True  -> apt002, apt003 <매일아침 9시에 Lambda 발송>
                      -> apt001, apt004 <메뉴얼 람다 실행으로 발송>      
                False -> 아직 해당 사항 없음 (실시간 푸쉬 발송)
            """
            is_pending = True
            message_dict = MessageConverter.to_dict(message_dto)
            notification_dict = dict(
                user_id=target_user.id,
                token=target_user.device.device_token.token,
                endpoint=target_user.device.endpoint,
                uuid=target_user.device.uuid,
                topic=topic,
                badge_type=NotificationBadgeTypeEnum.ALL.value,
                message=message_dict,
                is_read=False,
                is_pending=is_pending,
                status=NotificationStatusEnum.WAIT.value,
            )

            notification_list.append(notification_dict)

        return notification_list
