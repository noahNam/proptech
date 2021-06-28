from typing import Optional, List, Union

from sqlalchemy import exc, exists

from app.extensions.utils.log_helper import logger_

from app.extensions.database import session
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import (
    InterestRegionModel,
    InterestRegionGroupModel,
    DeviceModel,
    DeviceTokenModel,
    AppAgreeTermsModel,
    UserProfileModel,
    UserInfoModel,
)
from app.persistence.model import UserModel
from core.domains.authentication.dto.sms_dto import MobileAuthConfirmSmsDto
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto,
)
from core.domains.user.entity.user_entity import UserInfoEntity, UserInfoEmptyEntity
from core.exceptions import NotUniqueErrorException

logger = logger_.getLogger(__name__)


class UserRepository:
    def create_user(self, dto: CreateUserDto) -> None:
        try:
            user = UserModel(
                id=dto.user_id,
                is_required_agree_terms=dto.is_required_agree_terms,
                is_active=dto.is_active,
                is_out=dto.is_out,
            )
            session.add(user)
            session.commit()
        except exc.IntegrityError as e:
            logger.error(
                f"[UserRepository][create_user] user_id : {dto.user_id} error : {e}"
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
                f"[UserRepository][create_interest_regions] user_id : {dto.user_id} error : {e}"
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
                f"[UserRepository][update_interest_region_group_counts] user_id : {dto.user_id} error : {e}"
            )

    def _create_interest_region_objects(
            self, dto: CreateUserDto
    ) -> List[InterestRegionModel]:
        return [
            InterestRegionModel(user_id=dto.user_id, region_id=region_id)
            for region_id in dto.region_ids
        ]

    def create_device(self, dto: CreateUserDto) -> Optional[int]:
        try:
            device = DeviceModel(
                user_id=dto.user_id,
                uuid=dto.uuid,
                os=dto.os,
                is_active=dto.is_active_device,
                is_auth=dto.is_auth,
            )
            session.add(device)
            session.commit()

            return device.id
        except exc.IntegrityError as e:
            logger.error(
                f"[UserRepository][create_devices] user_id : {dto.user_id} error : {e}"
            )
            session.rollback()
            raise NotUniqueErrorException(type_="T002")

    def create_device_token(self, dto: CreateUserDto, device_id) -> None:
        try:
            device_token = DeviceTokenModel(device_id=device_id, token=dto.token, )
            session.add(device_token)
            session.commit()
        except exc.IntegrityError as e:
            logger.error(
                f"[UserRepository][create_device_token] user_id : {dto.user_id} error : {e}"
            )
            session.rollback()
            raise NotUniqueErrorException(type_="T003")

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

    def create_app_agree_terms(self, dto: CreateAppAgreeTermsDto) -> None:
        try:
            receipt_marketing_date = (
                get_server_timestamp() if dto.receipt_marketing_yn else None
            )

            user = AppAgreeTermsModel(
                user_id=dto.user_id,
                private_user_info_yn=dto.private_user_info_yn,
                required_terms_yn=dto.required_terms_yn,
                receipt_marketing_yn=dto.receipt_marketing_yn,
                receipt_marketing_date=receipt_marketing_date,
            )
            session.add(user)
            session.commit()
        except exc.IntegrityError as e:
            logger.error(
                f"[UserRepository][create_app_agree_terms] user_id : {dto.user_id} error : {e}"
            )
            session.rollback()
            raise NotUniqueErrorException(type_="T004")

    def update_user_required_agree_terms(self, dto: CreateAppAgreeTermsDto) -> None:
        try:
            session.query(UserModel).filter_by(id=dto.user_id).update(
                {"is_required_agree_terms": True}
            )
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_required_agree_terms] user_id : {dto.user_id} error : {e}"
            )
            raise NotUniqueErrorException(type_="T005")

    def get_user_profile_id(self, dto: UpsertUserInfoDto) -> Optional[int]:
        user_profile = (
            session.query(UserProfileModel.id).filter_by(user_id=dto.user_id).first()
        )
        if not user_profile:
            return None

        return user_profile.id

    def is_user_info(self, dto: UpsertUserInfoDto) -> Optional[UserInfoEntity]:
        return session.query(
            exists()
                .where(UserInfoModel.user_profile_id == dto.user_profile_id)
                .where(UserInfoModel.code == dto.code)
        ).scalar()

    def create_user_nickname(self, dto: UpsertUserInfoDto) -> int:
        try:
            user_profile = UserProfileModel(
                user_id=dto.user_id, nickname=dto.value, last_update_code=dto.code
            )

            session.add(user_profile)
            session.commit()

            return user_profile.id
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[UserRepository][create_user_profiles] user_id : {dto.user_id} error : {e}"
            )
            raise NotUniqueErrorException(type_="T006")

    def update_user_nickname(self, dto: UpsertUserInfoDto):
        try:
            session.query(UserProfileModel).filter_by(id=dto.user_profile_id).update(
                {"nickname": dto.value, "last_update_code": dto.code}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_nickname] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def create_user_info(self, dto: UpsertUserInfoDto) -> None:
        try:
            user_info = UserInfoModel(
                user_profile_id=dto.user_profile_id, code=dto.code, value=dto.value
            )
            session.add(user_info)
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[UserRepository][create_user_info] user_id : {dto.user_id} error : {e}"
            )
            raise NotUniqueErrorException(type_="T007")

    def update_user_info(self, dto: UpsertUserInfoDto) -> None:
        try:
            session.query(UserInfoModel).filter_by(
                user_profile_id=dto.user_profile_id, code=dto.code
            ).update({"value": dto.value})
            session.commit()

            user_info_model2 = (
                session.query(UserInfoModel)
                    .filter_by(user_profile_id=dto.user_profile_id, code=dto.code)
                    .first()
            )
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_info] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def update_last_code_to_user_info(self, dto: UpsertUserInfoDto) -> None:
        try:
            session.query(UserProfileModel).filter_by(user_id=dto.user_id).update(
                {"last_update_code": dto.code}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_nickname] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def get_user_info(
            self, dto: GetUserInfoDto
    ) -> Union[UserInfoEntity, UserInfoEmptyEntity]:
        user_info = (
            session.query(UserInfoModel)
                .filter_by(user_profile_id=dto.user_profile_id, code=dto.code)
                .first()
        )

        if not user_info:
            return UserInfoEmptyEntity(code=dto.code)

        return user_info.to_entity()
