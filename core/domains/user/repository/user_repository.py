from typing import Optional, List

from sqlalchemy import exc

from app.extensions.utils.log_helper import logger_

from app.extensions.database import session
from app.persistence.model import (
    InterestRegionModel,
    InterestRegionGroupModel,
    DeviceModel,
)
from app.persistence.model import UserModel
from core.domains.authentication.dto.sms_dto import MobileAuthConfirmSmsDto
from core.domains.user.dto.user_dto import CreateUserDto, CreateUserProfileImgDto
from core.exceptions import NotUniqueErrorException

logger = logger_.getLogger(__name__)


class UserRepository:
    def create_user(self, dto: CreateUserDto) -> None:
        try:
            user = UserModel(
                id=dto.id,
                nickname=dto.nickname,
                email=dto.email,
                birthday=dto.birthday,
                gender=dto.gender,
                is_active=dto.is_active,
                is_out=dto.is_out,
            )
            session.add(user)
            session.commit()
        except exc.IntegrityError as e:
            logger.error(
                f"[UserRepository][create_user] user_id : {dto.id} error : {e}"
            )
            session.rollback()
            raise NotUniqueErrorException(type_="T001")

    def create_interest_regions(self, dto: CreateUserDto) -> None:
        try:
            interest_regions: List[
                InterestRegionModel
            ] = self._create_interest_region_objects(dto)
            if interest_regions:
                session.add_all(interest_regions)
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][create_interest_regions] user_id : {dto.id} error : {e}"
            )

    def update_interest_region_group_counts(self, dto: CreateUserDto) -> None:
        try:
            interest_regions: List[
                InterestRegionModel
            ] = self._create_interest_region_objects(dto)
            for interest_region in interest_regions:
                session.query(InterestRegionGroupModel).filter_by(
                    id=interest_region.region_id
                ).update(
                    {"interest_count": InterestRegionGroupModel.interest_count + 1}
                )
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_interest_region_group_counts] user_id : {dto.id} error : {e}"
            )

    def _create_interest_region_objects(
            self, dto: CreateUserDto
    ) -> List[InterestRegionModel]:
        return [
            InterestRegionModel(user_id=dto.id, region_id=region_id)
            for region_id in dto.region_ids
        ]

    def update_user_profile_img_id(self, user_id: int, profile_img_id: int) -> None:
        try:
            session.query(UserModel).filter_by(id=user_id).update(
                {"profile_img_id": profile_img_id}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_profile_img_id] user_id : {user_id} error : {e}"
            )

    def update_user_mobile_auth_info(self, dto: MobileAuthConfirmSmsDto) -> None:
        try:
            session.query(DeviceModel).filter_by(user_id=dto.user_id).update(
                {"phone_number": dto.phone_number, "is_auth": True}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_mobile_auth_info] user_id : {dto.user_id} error : {e}"
            )
