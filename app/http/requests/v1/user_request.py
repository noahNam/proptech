import json
from typing import List

from pydantic import BaseModel, StrictInt, StrictStr, ValidationError

from app.extensions.utils.log_helper import logger_
from core.domains.user.dto.user_dto import CreateUserDto
from core.domains.user.enum.user_enum import UserDefaultValueEnum
from core.exceptions import InvalidRequestException

logger = logger_.getLogger(__name__)


class CreateUserSchema(BaseModel):
    id: StrictInt
    nickname: StrictStr
    email: StrictStr
    birthday: StrictStr
    gender: StrictStr
    is_active: bool
    is_out: bool
    region_ids: List[int]
    file: List


class CreateUserSchemeRequest:
    def __init__(
        self, id, nickname, email, birthday, gender, region_ids, file,
    ):
        self.id = int(id) if id else None
        self.nickname = nickname if nickname else UserDefaultValueEnum.NICKNAME.value
        self.email = email
        self.birthday = birthday
        self.gender = gender if gender else None
        self.is_active = True
        self.is_out = False
        self.region_ids = json.loads(region_ids) if region_ids else []
        self.file = file

    def validate_request_and_make_dto(self):
        try:
            schema = CreateUserSchema(
                id=self.id,
                nickname=self.nickname,
                email=self.email,
                birthday=self.birthday,
                gender=self.gender,
                is_active=self.is_active,
                is_out=self.is_out,
                region_ids=self.region_ids,
                file=self.file,
            ).dict()
            return CreateUserDto(**schema)
        except ValidationError as e:
            logger.error(
                f"[CreateUserSchemeRequest][validate_request_and_make_dto] error : {e}"
            )
            raise InvalidRequestException(message=e.errors())
