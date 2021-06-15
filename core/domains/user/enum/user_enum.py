from enum import Enum


class UserDefaultValueEnum(Enum):
    NICKNAME = "unknown"


class UserInterestedHouseType(Enum):
    SUBSCRIPTION = 1
    RENT = 2
    BUY_HOUSE = 3
