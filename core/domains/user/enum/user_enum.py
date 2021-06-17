from enum import Enum


class UserDefaultValueEnum(Enum):
    NICKNAME = "unknown"


class UserHomeOwnerType(Enum):
    OWNER = 1
    NOT_OWNER = 2
    BEFORE_OWNER = 3  # 과거에는 있었지만 현재는 없다.


class UserInterestedHouseType(Enum):
    SUBSCRIPTION = 1
    RENT = 2
    BUY_HOUSE = 3
