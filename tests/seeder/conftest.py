import pytest
from datetime import date, timedelta, datetime
from faker import Faker

from app.extensions.utils.message_converter import MessageConverter
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.notification.dto.notification_dto import PushMessageDto
from core.domains.notification.enum.notification_enum import NotificationBadgeTypeEnum, NotificationTopicEnum
from tests.seeder.factory import (
    UserFactory,
    InterestRegionFactory,
    InterestRegionGroupFactory,
    UserProfileFactory,
    AvgMonthlyIncomeWorkerFactory,
    SidoCodeFactory, NotificationFactory, InterestHouseFactory
)

MODEL_FACTORIES = [
    UserFactory,
    InterestRegionFactory,
    InterestRegionGroupFactory,
    UserProfileFactory,
    AvgMonthlyIncomeWorkerFactory,
    SidoCodeFactory,
    NotificationFactory,
    InterestHouseFactory
]

faker = Faker()


@pytest.fixture
def create_users(session, user_factory):
    users = user_factory.build_batch(size=3)
    session.add_all(users)
    session.commit()

    return users


@pytest.fixture
def create_sido_codes(session, sido_code_factory):
    sido_code_1 = sido_code_factory.build(sido_code=11, sido_name='서울특별시', sigugun_code='11010', sigugun_name='종로구')
    sido_code_2 = sido_code_factory.build(sido_code=11, sido_name='서울특별시', sigugun_code='11020', sigugun_name='중구')
    sido_code_3 = sido_code_factory.build(sido_code=11, sido_name='서울특별시', sigugun_code='11030', sigugun_name='용산구')
    sido_code_4 = sido_code_factory.build(sido_code=29, sido_name='세종특별자치시', sigugun_code='29010', sigugun_name='세종시')
    sido_code_5 = sido_code_factory.build(sido_code=31, sido_name='경기도', sigugun_code='31011', sigugun_name='수원시 장안구')
    sido_code_6 = sido_code_factory.build(sido_code=31, sido_name='경기도', sigugun_code='31012', sigugun_name='수원시 권선구')
    sido_code_7 = sido_code_factory.build(sido_code=31, sido_name='경기도', sigugun_code='31030', sigugun_name='의정부시')
    sido_code_8 = sido_code_factory.build(sido_code=33, sido_name='충청북도', sigugun_code='33320', sigugun_name='보은군')

    list = [sido_code_1, sido_code_2, sido_code_3, sido_code_4, sido_code_5, sido_code_6, sido_code_7, sido_code_8]
    session.add_all(list)
    session.commit()


@pytest.fixture
def create_interest_region_groups(session, interest_region_group_factory):
    interest_region_groups = interest_region_group_factory.build_batch(size=3)
    session.add_all(interest_region_groups)
    session.commit()

    return interest_region_groups


@pytest.fixture
def create_notifications(session, notification_factory):
    user_id = 1

    # 분양소식
    message_dto = PushMessageDto(
        title="분양소식",
        content="관심 설정 해두신 동탄 메르시 분양이 시작됐습니다.",
        created_at=str(get_server_timestamp().replace(microsecond=0)),
        badge_type=NotificationBadgeTypeEnum.ALL.value,
        data={
            "user_id": user_id,
            "topic": NotificationTopicEnum.SUB_NEWS.value,
        },
    )
    # make notification message
    message_dict_1 = MessageConverter.to_dict(message_dto)

    # 분양일정
    message_dto = PushMessageDto(
        title="분양일정",
        content="관심 설정 해두신 동탄 메르시 신청 당일입니다.신청을 서둘러 주세요:)",
        created_at=str(get_server_timestamp().replace(microsecond=0)),
        badge_type=NotificationBadgeTypeEnum.ALL.value,
        data={
            "user_id": user_id,
            "topic": NotificationTopicEnum.SUB_SCHEDULE.value,
        },
    )
    # make notification message
    message_dict_2 = MessageConverter.to_dict(message_dto)

    # 공지사항
    message_dto = PushMessageDto(
        title="공지사항",
        content="2.0버전이 출시되었습니다.업데이트 요청 드립니다.",
        created_at=str(get_server_timestamp().replace(microsecond=0)),
        badge_type=NotificationBadgeTypeEnum.ALL.value,
        data={
            "user_id": user_id,
            "topic": NotificationTopicEnum.OFFICIAL.value,
        },
    )
    # make notification message
    message_dict_3 = MessageConverter.to_dict(message_dto)

    notification_1 = notification_factory.build(message=message_dict_1, topic=NotificationTopicEnum.SUB_NEWS.value)
    notification_2 = notification_factory.build(message=message_dict_2, topic=NotificationTopicEnum.SUB_SCHEDULE.value)
    notification_3 = notification_factory.build(message=message_dict_3, topic=NotificationTopicEnum.OFFICIAL.value)

    notifications = [notification_1, notification_2, notification_3]
    session.add_all(notifications)
    session.commit()

    return notifications


def make_random_today_date(between_days: int = 1, year_ago: int = 2):
    """
    주어진 날의 00:00:00 ~ 23:59:59 사이의 랜덤 시간을 만든다.
    기본적으로 조회시간 기준 2년전으로 만듬
    """
    return faker.date_time_between_dates(
        datetime_start=date.today() - timedelta(days=365 * year_ago + between_days),
        datetime_end=datetime.now() - timedelta(days=365 * year_ago + between_days),
    )


def make_random_between_date(start_date, end_date):
    """주어진 날짜 사이의 랜덤 date 만든다"""
    return faker.date_time_between_dates(
        datetime_start=start_date, datetime_end=end_date
    )
