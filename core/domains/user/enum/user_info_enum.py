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
    COND_1_CD = 1
    COND_1_NM = "있어요"
    COND_2_CD = 2
    COND_2_NM = "없어요"
    COND_3_CD = 3
    COND_3_NM = "과거에 있었지만 현재는 처분했어요"


class IsHouseHolderCodeEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "예"
    COND_2_CD = 2
    COND_2_NM = "아니요"


class IsMarriedCodeEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "기혼(외벌이)"
    COND_2_CD = 2
    COND_2_NM = "기혼(맞벌이)"
    COND_3_CD = 3
    COND_3_NM = "미혼"
    COND_4_CD = 4
    COND_4_NM = "한부모"


class NumberDependentsEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "1명"
    COND_2_CD = 2
    COND_2_NM = "2명"
    COND_3_CD = 3
    COND_3_NM = "3명"
    COND_4_CD = 4
    COND_4_NM = "4명"
    COND_5_CD = 5
    COND_5_NM = "5명"
    COND_6_CD = 6
    COND_6_NM = "6명 이상"
    COND_7_CD = 7
    COND_7_NM = "없어요"


class IsChildEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "있어요"
    COND_2_CD = 2
    COND_2_NM = "없어요"


class IsSubAccountEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "있어요"
    COND_2_CD = 2
    COND_2_NM = "없어요"


class MonthlyIncomeEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "70%"
    COND_2_CD = 2
    COND_2_NM = "80%"
    COND_3_CD = 3
    COND_3_NM = "100%"
    COND_4_CD = 4
    COND_4_NM = "110%"
    COND_5_CD = 5
    COND_5_NM = "120%"
    COND_6_CD = 6
    COND_6_NM = "130%"
    COND_7_CD = 7
    COND_7_NM = "140%"


class AssetsRealEstateEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "12,600만원 이하"
    COND_2_CD = 2
    COND_2_NM = "21,550만원 이하"
    COND_3_CD = 3
    COND_3_NM = "21,550만원 초과"
    COND_4_CD = 4
    COND_4_NM = "없음"


class AssetsCarEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "2,494만원 이하"
    COND_2_CD = 2
    COND_2_NM = "2,797만원 이하"
    COND_3_CD = 3
    COND_3_NM = "2,797만원 초과"
    COND_4_CD = 4
    COND_4_NM = "없음"


class AssetsTotalEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "21,500만원 이하"
    COND_2_CD = 2
    COND_2_NM = "25,400만원 이하"
    COND_3_CD = 3
    COND_3_NM = "29,200만원 이하"
    COND_4_CD = 4
    COND_4_NM = "29,200만원 초과"
    COND_5_CD = 5
    COND_5_NM = "없음"


class SpecialCondEnum(Enum):
    COND_1_CD = 1
    COND_1_NM = "공통"
    COND_2_CD = 2
    COND_2_NM = "국민주택"
    COND_3_CD = 3
    COND_3_NM = "민영주택"
    COND_4_CD = 4
    COND_4_NM = "없음"
