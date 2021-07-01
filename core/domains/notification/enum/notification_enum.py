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
    APT01 = "apt01"
