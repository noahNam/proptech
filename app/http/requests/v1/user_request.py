import json
from typing import List

from pydantic import BaseModel, StrictInt, StrictStr, ValidationError

from app.extensions.utils.log_helper import logger_
from core.domains.user.dto.user_dto import CreateUserDto
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class CreateUserSchema(BaseModel):
    user_id: StrictInt
    is_required_agree_terms: bool
    is_active: bool
    is_out: bool
    region_ids: List[int] = []
    uuid: str
    os: str
    is_active_device: bool
    is_auth: bool
    token: str


class CreateUserSchemeRequest:
    def __init__(
        self,
        user_id,
        region_ids,
        uuid,
        os,
        token,
    ):
        self.user_id = int(user_id) if user_id else None
        self.is_required_agree_terms = False
        self.is_active = True
        self.is_out = False
        self.region_ids = json.loads(region_ids) if region_ids else []
        self.uuid = uuid
        self.os = os
        self.is_active_device = True
        self.is_auth = False
        self.token = token

    def validate_request_and_make_dto(self):
        try:
            schema = CreateUserSchema(
                user_id=self.user_id,
                is_required_agree_terms=self.is_required_agree_terms,
                is_active=self.is_active,
                is_out=self.is_out,
                region_ids=self.region_ids,
                uuid=self.uuid,
                os=self.os,
                is_active_device=self.is_active_device,
                is_auth=self.is_auth,
                token=self.token,
            ).dict()
            return CreateUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[CreateUserSchemeRequest][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
