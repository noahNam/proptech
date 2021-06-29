from enum import Enum


class CodeEnum(Enum):
    NICKNAME = "1000"
    BIRTHDAY = "1001"
    ADDRESS_LV1 = "1002"
    ADDRESS_LV2 = "1003"
    ADDRESS_DATE = "1004"
    IS_HOUSE_OWNER = "1005"
    SELL_HOUSE_DATE = "1006"
    IS_HOUSE_HOLDER = "1007"
    IS_MARRIED = "1008"
    MARRIAGE_REG_DATE = "1009"
    NUMBER_DEPENDENTS = "1010"
    IS_CHILD = "1011"
    CHILD_AGE_SIX = "1012"
    CHILD_AGE_NINETEEN = "1013"
    CHILD_AGE_TWENTY = "1014"
    IS_SUB_ACCOUNT = "1015"
    SUB_ACCOUNT_DATE = "1016"
    SUB_ACCOUNT_TIMES = "1017"
    SUB_ACCOUNT_TOTAL_PRICE = "1018"
    MONTHLY_INCOME = "1019"
    ASSETS_REAL_ESTATE = "1020"
    ASSETS_CAR = "1021"
    ASSETS_TOTAL = "1022"
    IS_SUPPORT_PARENT = "1023"
    SUPPORT_PARENT_DATE = "1024"
    SPECIAL_COND = "1025"


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
    COND_CD = [1, 2]
    COND_NM = ["있어요", "없어요"]


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
    COND_CD_1 = [50, 70, 80, 100, 120, 130]
    COND_NM_1 = []

    # 2020년 맞벌이 기준
    COND_CD_2 = [50, 80, 110, 120, 130, 140]
    COND_NM_2 = []


class AssetsRealEstateEnum(Enum):
    COND_CD = [1, 2, 3, 4]
    COND_NM = ["12,600만원 이하", "21,550만원 이하", "21,550만원 초과", "없음"]


class AssetsCarEnum(Enum):
    COND_CD = [1, 2, 3, 4]
    COND_NM = ["2,494만원 이하", "2,797만원 이하", "2,797만원 초과", "없음"]


class AssetsTotalEnum(Enum):
    COND_CD = [1, 2, 3, 4, 5]
    COND_NM = ["21,500만원 이하", "25,400만원 이하", "29,200만원 이하", "29,200만원 초과", "없음"]


class SpecialCondEnum(Enum):
    COND_CD = [1, 2, 3, 4]
    COND_NM = ["공통", "국민주택", "민영주택", "없음"]
