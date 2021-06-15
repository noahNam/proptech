from enum import Enum


class RedisKeyPrefix(Enum):
    MOBILE_AUTH = "mobile_auth"


class RedisExpire(Enum):
    MOBILE_AUTH_TIME = 180
