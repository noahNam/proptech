import os
import uuid
from typing import Optional, List

from sqlalchemy import exc

from app.extensions.utils.enum.aws_enum import S3PathEnum, S3BucketEnum
from app.extensions.utils.image_helper import S3Helper
from app.extensions.utils.log_helper import logger_

from app.extensions.database import session
from app.persistence.model import InterestRegionModel, UserProfileImgModel
from app.persistence.model import UserModel
from core.domains.user.dto.user_dto import CreateUserDto, CreateUserProfileImgDto
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

    # def upload_user_profile_img(self, dto: CreateUserDto) -> None:
    #     for file in dto.files:
    #         f, extension = os.path.splitext(file.filename)
    #         uuid_ = str(uuid.uuid4())
    #         object_name = S3PathEnum.PROFILE_IMGS.value + uuid_ + extension
    #
    #         res = S3Helper.upload(
    #             bucket=S3BucketEnum.APARTALK_BUCKET.value,
    #             file_name=file,
    #             object_name=object_name,
    #         )
    #
    #         if not res:
    #             return False
    #
    #         attachment = self._user_repo.update_user_profile(
    #             user_profile_id=user_profile_id,
    #             file_name=f,
    #             path=S3PathEnum.POST_IMGS.value,
    #             extension=extension,
    #             uuid=uuid_,
    #         )
    #         if not attachment:
    #             return False
    #         attachment_list.append(attachment)
    #
    #     return attachment_list

    def create_user_profile_img(
            self, dto: CreateUserProfileImgDto
    ) -> Optional[int]:
        try:
            user_profile_img = UserProfileImgModel(
                uuid=dto.uuid_,
                file_name=dto.file_name,
                path=dto.path,
                extension=dto.extension,
            )
            session.add(user_profile_img)
            session.commit()

            return user_profile_img.id
        except exc.IntegrityError as e:
            logger.error(
                f"[UserRepository][update_user_profile_img] user_id : {dto.user_id} error : {e}"
            )
            session.rollback()
            raise NotUniqueErrorException
