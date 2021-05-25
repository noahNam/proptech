from enum import Enum


class NotificationStatusEnum(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class NotificationBadgeTypeEnum(Enum):
    ALL = "all"
    IN = "in"
    OUT = "out"


class DeviceTypeEnum(Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
