from typing import Optional

from pydantic import BaseModel, StrictInt, ValidationError, validator

from app.extensions.utils.log_helper import logger_
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto,
    GetUserDto,
    UpdateUserProfileDto,
)
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class GetUserSchema(BaseModel):
    user_id: StrictInt


class CreateUserSchema(BaseModel):
    user_id: StrictInt
    email: Optional[str]
    phone_number: Optional[str]
    is_required_agree_terms: bool
    is_active: bool
    is_out: bool
    uuid: str
    os: str
    is_active_device: bool
    is_auth: bool
    token: str

    @validator("phone_number")
    def check_phone_number(cls, phone_number) -> Optional[str]:
        if not phone_number:
            return None

        phone_number = "".join(phone_number.split("-"))
        if len(phone_number) > 11:
            raise ValidationError
        return phone_number


class CreateAppAgreeTermsSchema(BaseModel):
    user_id: StrictInt
    private_user_info_yn: bool
    required_terms_yn: bool
    receive_marketing_yn: bool


class UpsertUserInfoSchema(BaseModel):
    user_id: StrictInt
    codes: list
    values: list = []


class GetUserInfoSchema(BaseModel):
    user_id: StrictInt
    survey_step: StrictInt


class GetUserMainSchema(BaseModel):
    user_id: StrictInt


class GetSurveyResultSchema(BaseModel):
    user_id: StrictInt


class UpdateUserProfileSchema(BaseModel):
    user_id: StrictInt
    nickname: str


class GetUserRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetUserSchema(user_id=self.user_id, ).dict()
            return GetUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetUserRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class CreateUserRequestSchema:
    def __init__(
            self, user_id, uuid, os, token, email, phone_number
    ):
        self.user_id = int(user_id) if user_id else None
        self.email = email
        self.phone_number = phone_number
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


class GetUserMainRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetUserMainSchema(user_id=self.user_id, ).dict()
            return GetUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetUserMainRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetSurveyResultRequestSchema:
    def __init__(self, user_id):
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetSurveyResultSchema(user_id=self.user_id, ).dict()
            return GetUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetSurveyResultRequestSchema][validate_request_and_make_dto] error : {e}"
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
