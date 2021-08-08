from pydantic import BaseModel, ValidationError, validator

from app.extensions.utils.log_helper import logger_
from core.domains.banner.dto.banner_dto import GetHomeBannerDto, SectionTypeDto
from core.domains.banner.enum.banner_enum import SectionType
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class GetHomeBannerSchema(BaseModel):
    section_type: int
    user_id: int

    @validator("section_type")
    def check_section_type(cls, section_type) -> str:
        if section_type != SectionType.HOME_SCREEN.value:
            raise ValidationError("Invalid section_type: need home_screen value")
        return section_type


class GetHomeBannerRequestSchema:
    def __init__(self, section_type, user_id):
        self.section_type = section_type
        self.user_id = int(user_id) if user_id else None

    def validate_request_and_make_dto(self):
        try:
            schema = GetHomeBannerSchema(
                section_type=int(self.section_type), user_id=self.user_id
            ).dict()
            return GetHomeBannerDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetHomeBannerRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())


class GetPreSubscriptionBannerSchema(BaseModel):
    section_type: int

    @validator("section_type")
    def check_section_type(cls, section_type) -> str:
        if section_type != SectionType.PRE_SUBSCRIPTION_INFO.value:
            raise ValidationError("Invalid section_type: need pre_subscription value")
        return section_type


class GetPreSubscriptionBannerRequestSchema:
    def __init__(self, section_type):
        self.section_type = section_type

    def validate_request_and_make_dto(self):
        try:
            schema = GetPreSubscriptionBannerSchema(
                section_type=int(self.section_type)
            ).dict()
            return SectionTypeDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[GetPreSubscriptionBannerRequestSchema][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
