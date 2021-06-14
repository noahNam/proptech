import hashlib
import hmac
import base64
import json
import time
from typing import Any

import requests
from flask import Flask

from app.extensions.utils.enum.ncp_enum import SmsServiceEnum
from app.extensions.utils.log_helper import logger_
from core.domains.authentication.dto.sms_dto import SendSmsDto

logger = logger_.getLogger(__name__)


class SmsClient:
    SID = "SENS_SID"
    ACCESS_KEY = "NCP_ACCESS_KEY"
    SECRET_KEY = "NCP_SECRET_KEY"

    def __init__(self):
        self._sms_uri = None
        self._sms_url = None
        self._sid = None
        self._access_key = None
        self._secret_key = None

    def init_app(self, app: Flask):
        self._sid = app.config.get(SmsClient.SID)
        self._sms_uri = SmsServiceEnum.SMS_URI.value.format(self._sid)
        self._sms_url = SmsServiceEnum.SMS_URL.value.format(self._sms_uri)
        self._access_key = app.config.get(SmsClient.ACCESS_KEY)
        self._secret_key = app.config.get(SmsClient.SECRET_KEY)

    def make_signature(self) -> SendSmsDto:
        sms_uri = self._sms_uri

        timestamp = int(time.time() * 1000)
        timestamp = str(timestamp)

        access_key = self._access_key
        secret_key = self._secret_key
        secret_key = bytes(secret_key, 'UTF-8')

        method = "POST"

        message = method + " " + sms_uri + "\n" + timestamp + "\n" + access_key
        message = bytes(message, 'UTF-8')
        signing_key = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

        return SendSmsDto(
            signing_key=signing_key,
            timestamp=timestamp
        )

    def convert_message(self, content: str, to_number: str):
        return {
            'type': 'SMS',
            'countryCode': '82',
            'from': SmsServiceEnum.FROM_NUMBER.value,
            'contentType': 'COMM',
            'content': content,
            'messages': [{'to': "{}".format(to_number)}]
        }

    def send_sms(self, dto: SendSmsDto) -> Any:
        try:
            response = requests.post(
                self._sms_url,
                headers={"Content-Type": "application/json; charset=utf-8",
                         "x-ncp-apigw-timestamp": dto.timestamp,
                         "x-ncp-iam-access-key": self._access_key,
                         "x-ncp-apigw-signature-v2": dto.signing_key,
                         },
                data=json.dumps(dto.message)
            )

            return dict(status_code=response.status_code, message=response.reason)
        except Exception as e:
            logger.error(
                f"[SmsClient][send_sms] error : {e}"
            )