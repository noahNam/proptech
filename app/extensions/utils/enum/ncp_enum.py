from enum import Enum


class SmsServiceEnum(Enum):
    SMS_URI = "/sms/v2/services/{}/messages"
    SMS_URL = "https://sens.apigw.ntruss.com{}"
    FROM_NUMBER = "01044744412"


class SmsMessageEnum(Enum):
    SMS_AUTH_MESSAGE = "[토드홈][{}] 인증번호 4자리를 입력해주세요."
