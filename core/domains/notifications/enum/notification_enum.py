from enum import Enum


class NotificationStatusEnum(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class DeviceTypeEnum(Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
