from enum import Enum


class NotificationStatusEnum(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    WAIT = "wait"


class NotificationBadgeTypeEnum(Enum):
    ALL = "all"
    IN = "in"
    OUT = "out"


class DeviceTypeEnum(Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


class NotificationCategoryEnum(Enum):
    APT01 = "apt01"
