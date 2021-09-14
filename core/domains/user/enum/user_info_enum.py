from enum import Enum


class CodeEnum(Enum):
    NICKNAME = 1000
    BIRTHDAY = 1001
    ADDRESS = 1002
    ADDRESS_DETAIL = 1003
    ADDRESS_DATE = 1004
    IS_HOUSE_OWNER = 1005
    SELL_HOUSE_DATE = 1006
    IS_HOUSE_HOLDER = 1007
    IS_MARRIED = 1008
    MARRIAGE_REG_DATE = 1009
    NUMBER_DEPENDENTS = 1010
    IS_CHILD = 1011
    CHILD_AGE_SIX = 1012
    CHILD_AGE_NINETEEN = 1013
    CHILD_AGE_TWENTY = 1014
    MOST_CHILD_YOUNG_AGE = 1015
    IS_SUB_ACCOUNT = 1016
    SUB_ACCOUNT_DATE = 1017
    SUB_ACCOUNT_TIMES = 1018
    SUB_ACCOUNT_TOTAL_PRICE = 1019

    MONTHLY_INCOME = 1020
    ASSETS_REAL_ESTATE = 1021
    ASSETS_CAR = 1022
    ASSETS_TOTAL = 1023
    IS_SUPPORT_PARENT = 1024
    SUPPORT_PARENT_DATE = 1025
    SPECIAL_COND = 1026


class CodeStepEnum(Enum):
    ONE = [
        1000,
        1001,
        1002,
        1003,
        1004,
        1005,
        1006,
        1007,
        1008,
        1009,
        1010,
        1011,
        1012,
        1013,
        1014,
        1016,
        1017,
        1018,
        1019,
    ]
    TWO = [1020, 1021, 1022, 1023, 1024, 1025, 1026]
    COMPLETE_ONE = 1019
    COMPLETE_TWO = 1026


class AddressCodeEnum(Enum):
    COND_CD = []
    COND_NM = []


class AddressDetailCodeEnum(Enum):
    COND_CD = []
    COND_NM = []


class IsHouseOwnerCodeEnum(Enum):
    COND_CD = [1, 2, 3]
    COND_NM = ["있어요", "없어요", "과거에 있었지만 현재는 처분했어요"]


class IsHouseHolderCodeEnum(Enum):
    COND_CD = [1, 2]
    COND_NM = ["예", "아니요"]


class IsMarriedCodeEnum(Enum):
    COND_CD = [1, 2, 3, 4]
    COND_NM = ["기혼(외벌이)", "기혼(맞벌이)", "미혼", "한부모"]


class NumberDependentsEnum(Enum):
    COND_CD = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    COND_NM = ["1명", "2명", "3명", "4명", "5명", "6명", "7명", "8명", "없어요"]


class IsChildEnum(Enum):
    COND_CD = [1, 2, 3, 4]
    COND_NM = ["자녀 1명", "자녀 2명", "자녀 3명 이상", "없어요"]


class IsSubAccountEnum(Enum):
    COND_CD = [1, 2]
    COND_NM = ["있어요", "없어요"]


class MonthlyIncomeEnum(Enum):
    # # 외벌이 기준
    # COND_CD_1 = [1, 2, 3, 4, 5, 6]
    # COND_NM_1 = ["50%", "70%", "80%", "100%", "120%", "130%"]
    #
    # # 맞벌이 기준
    # COND_CD_2 = [1, 2, 3, 4, 5, 6]
    # COND_NM_2 = ["50%", "80%", "110%", "120%", "130%", "140%"]

    # 2020년 외벌이 기준
    COND_CD_1 = [50, 70, 80, 100, 110, 120, 130, 140, 0]
    COND_NM_1 = []

    # 2020년 맞벌이 기준
    COND_CD_2 = [50, 80, 110, 120, 130, 140, 160, 0]
    COND_NM_2 = []


class AssetsRealEstateEnum(Enum):
    COND_CD = [1, 2, 3]
    COND_NM = ["없어요", "215,500천원 이하", "215,500천원 초과"]


class AssetsCarEnum(Enum):
    COND_CD = [1, 2, 3]
    COND_NM = ["없어요", "34,960천원 이하", "34,960천원 초과"]


class AssetsTotalEnum(Enum):
    COND_CD = [1, 2, 3, 4, 5]
    COND_NM = ["없어요", "215,500천원 이하", "250,460천원 이하", "307,000천원 이하", "307,000천원 초과"]


class IsSupportParentCodeEnum(Enum):
    COND_CD = [1, 2]
    COND_NM = ["예", "아니요"]


class SpecialCondEnum(Enum):
    COND_CD = [1, 2, 3]
    COND_NM = ["없음", "기관 추천 특별공급", "기타"]
