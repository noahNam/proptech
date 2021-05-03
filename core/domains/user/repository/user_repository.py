from typing import Optional, List

from sqlalchemy import exc

from app.extensions.utils.log_helper import logger_

from app.extensions.database import session
from app.persistence.model import InterestRegionModel
from app.persistence.model import UserModel
from core.domains.user.dto.user_dto import CreateUserDto
from core.domains.user.entity.user_entity import UserEntity
from core.exceptions import NotUniqueErrorException

logger = logger_.getLogger(__name__)


class UserRepository:
    def get_user(self, user_id: int) -> Optional[UserEntity]:
        user = session.query(UserModel).filter_by(id=user_id).first()
        pass

    def create_user(self, dto: CreateUserDto) -> None:
        try:
            user = UserModel(
                id=dto.id,
                nickname=dto.nickname,
                email=dto.email,
                birthday=dto.birthday,
                gender=dto.gender,
                is_active=dto.is_active,
                is_out=dto.is_out
            )
            session.add(user)

            interest_regions: List[InterestRegionModel] = self._create_interest_region_objects(dto)
            if interest_regions:
                session.add_all(interest_regions)

            session.commit()
        except exc.IntegrityError as e:
            logger.error(
                f"[UserRepository][create_user] user_id : {dto.id} error : {e}"
            )
            session.rollback()
            raise NotUniqueErrorException

    def _create_interest_region_objects(self, dto: CreateUserDto) -> List[InterestRegionModel]:
        return [
            InterestRegionModel(user_id=dto.id, region_id=region_id)
            for region_id in dto.region_ids
        ]
