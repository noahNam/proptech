from typing import Optional

from pydantic import (
    BaseModel,
    StrictInt,
    ValidationError,
    validator,
    StrictStr,
    StrictBool,
)

from app.extensions.utils.log_helper import logger_
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto,
    GetUserDto,
    UpdateUserProfileDto,
    GetUserProviderDto,
    GetMonthlyIncomesDto,
    UpdateFcmTokenDto,
)
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class GetUserSchema(BaseModel):
    user_id: StrictInt


class CreateUserSchema(BaseModel):
    user_id: StrictInt
    email: Optional[StrictStr]
    phone_number: Optional[StrictStr]
    is_required_agree_terms: StrictBool
    is_active: StrictBool
    is_out: StrictBool
    uuid: StrictStr
    os: StrictStr
    is_active_device: StrictBool
    is_auth: StrictBool
    token: StrictStr


class CreateAppAgreeTermsSchema(BaseModel):
    user_id: StrictInt
    private_user_info_yn: StrictBool
    required_terms_yn: StrictBool
    receive_marketing_yn: StrictBool


class UpsertUserInfoSchema(BaseModel):
    user_id: StrictInt
    codes: list
    values: list = []


class GetUserInfoSchema(BaseModel):
    user_id: StrictInt
    survey_step: StrictInt


class GetMonthlyIncomesSchema(BaseModel):
    user_id: StrictInt
    is_married: StrictStr
    number_dependents: StrictStr


class GetUserMainSchema(BaseModel):
    user_id: StrictInt


class GetSurveysSchema(BaseModel):
    user_id: StrictInt


class UpdateUserProfileSchema(BaseModel):
    user_id: StrictInt
    nickname: StrictStr


class GetUserProviderSchema(BaseModel):
    user_id: StrictInt
    auth_header: StrictStr


class UpdateFcmTokenSchema(BaseModel):
    user_id: StrictInt
    fcm_token: StrictStr


class GetUserRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetUserSchema(user_id=self.user_id,).dict()
            return GetUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetUserRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class CreateUserRequestSchema:
    def __init__(self, user_id, uuid, os, token, email=None, phone_number=None):
        self.user_id = int(user_id) if user_id else None
        self.email = email
        self.phone_number = phone_number if phone_number else None
        self.is_required_agree_terms = False
        self.is_active = True
        self.is_out = False
        self.uuid = uuid
        self.os = os
        self.is_active_device = True
        self.is_auth = False
        self.token = token

    def validate_request_and_make_dto(self):
        try:
            schema = CreateUserSchema(
                user_id=self.user_id,
                email=self.email,
                phone_number=self.phone_number,
                is_required_agree_terms=self.is_required_agree_terms,
                is_active=self.is_active,
                is_out=self.is_out,
                uuid=self.uuid,
                os=self.os,
                is_active_device=self.is_active_device,
                is_auth=self.is_auth,
                token=self.token,
            ).dict()
            return CreateUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[CreateUserRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class CreateAppAgreeTermsRequestSchema:
    def __init__(
        self, user_id, receive_marketing_yn,
    ):
        self.user_id = int(user_id) if user_id else None
        self.private_user_info_yn = True
        self.required_terms_yn = True
        self.receive_marketing_yn = receive_marketing_yn

    def validate_request_and_make_dto(self):
        try:
            schema = CreateAppAgreeTermsSchema(
                user_id=self.user_id,
                private_user_info_yn=self.private_user_info_yn,
                required_terms_yn=self.required_terms_yn,
                receive_marketing_yn=self.receive_marketing_yn,
            ).dict()
            return CreateAppAgreeTermsDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[CreateAppAgreeTermRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UpsertUserInfoRequestSchema:
    def __init__(
        self, user_id, codes, values,
    ):
        self.user_id = int(user_id) if user_id else None
        self.codes = codes
        self.values = values

    def validate_request_and_make_dto(self):
        try:
            schema = UpsertUserInfoSchema(
                user_id=self.user_id, codes=self.codes, values=self.values,
            ).dict()
            return UpsertUserInfoDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UpsertUserInfoRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetUserInfoRequestSchema:
    def __init__(
        self, user_id, survey_step,
    ):
        self.user_id = int(user_id) if user_id else None
        self.survey_step = int(survey_step)

    def validate_request_and_make_dto(self):
        try:
            schema = GetUserInfoSchema(
                user_id=self.user_id, survey_step=self.survey_step,
            ).dict()
            return GetUserInfoDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetUserInfoRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetMonthlyIncomesRequestSchema:
    def __init__(self, user_id, is_married, number_dependents):
        self.user_id = int(user_id) if user_id else None
        self.is_married = is_married
        self.number_dependents = number_dependents

    def validate_request_and_make_dto(self):
        try:
            schema = GetMonthlyIncomesSchema(
                user_id=self.user_id,
                is_married=self.is_married,
                number_dependents=self.number_dependents,
            ).dict()
            return GetMonthlyIncomesDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetMonthlyIncomeRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetUserMainRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetUserMainSchema(user_id=self.user_id,).dict()
            return GetUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetUserMainRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetSurveysRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetSurveysSchema(user_id=self.user_id,).dict()
            return GetUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetSurveysRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UpdateUserProfileRequestSchema:
    def __init__(self, user_id, nickname):
        self.user_id = int(user_id) if user_id else None
        self.nickname = nickname

    def validate_request_and_make_dto(self):
        try:
            schema = UpdateUserProfileSchema(
                user_id=self.user_id, nickname=self.nickname
            ).dict()
            return UpdateUserProfileDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UpdateUserProfileRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetUserProviderRequestSchema:
    def __init__(self, user_id, auth_header):
        self.user_id = int(user_id) if user_id else None
        self.auth_header = auth_header

    def validate_request_and_make_dto(self):
        try:
            schema = GetUserProviderSchema(
                user_id=self.user_id, auth_header=self.auth_header
            ).dict()
            return GetUserProviderDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetUserProviderRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class UpdateFcmTokenRequestSchema:
    def __init__(self, user_id, fcm_token):
        self.user_id = int(user_id) if user_id else None
        self.fcm_token = fcm_token

    def validate_request_and_make_dto(self):
        try:
            schema = UpdateFcmTokenSchema(
                user_id=self.user_id, fcm_token=self.fcm_token
            ).dict()
            return UpdateFcmTokenDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[UpdateFcmTokenRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
