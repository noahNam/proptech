from enum import Enum


class NotificationStatusEnum(Enum):
    WAIT = 0
    SUCCESS = 1
    FAILURE = 2


class NotificationBadgeTypeEnum(Enum):
    ALL = "all"
    IN = "in"
    OUT = "out"


class DeviceTypeEnum(Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


class NotificationPushTypeEnum(Enum):
    """
        Push 종류
        OFFICIAL = 공지 Push
        PRIVATE = 개인화 Push
        MARKETING = 마케 Push
    """
    OFFICIAL = "official"
    PRIVATE = "private"
    MARKETING = "marketing"


class NotificationTopicEnum(Enum):
    """
        Push 주제
        OFFICIAL = 공지
        SUB_NEWS = 모집공고일, 당첨자발표일
        SUB_SCHEDULE = 특별공급일, 1순위, 2순위 날짜
        MARKETING = 마케팅
    """
    OFFICIAL = "apt001"
    SUB_NEWS = "apt002"
    SUB_SCHEDULE = "apt003"
    MARKETING = "apt004"


class NotificationHistoryCategoryEnum(Enum):
    OFFICIAL = "official"
    MY = "my"
