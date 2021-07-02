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


class NotificationTopicEnum(Enum):
    OFFICIAL = "apt001"
    SUB_NEWS = "apt002"
    SUB_SCHEDULE = "apt003"


class NotificationHistoryCategoryEnum(Enum):
    OFFICIAL = "official"
    MY = "my"
