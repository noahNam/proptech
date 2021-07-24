from typing import Optional, List, Union

from sqlalchemy import exc, exists
from sqlalchemy.orm import joinedload

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import (
    DeviceModel,
    DeviceTokenModel,
    AppAgreeTermsModel,
    UserProfileModel,
    UserInfoModel,
    AvgMonthlyIncomeWokrerModel,
    SidoCodeModel,
    ReceivePushTypeModel,
    PointModel,
    UserModel,
    RecentlyViewModel
)
from core.domains.authentication.dto.sms_dto import MobileAuthConfirmSmsDto
from core.domains.notification.dto.notification_dto import UpdateReceiveNotificationSettingDto
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto,
    AvgMonthlyIncomeWokrerDto,
    UpsertUserInfoDetailDto,
    GetUserInfoDetailDto,
    GetUserDto, RecentlyViewDto,
)
from core.domains.user.entity.user_entity import UserInfoEntity, UserInfoEmptyEntity, UserEntity, \
    UserInfoCodeValueEntity
from core.domains.user.enum.user_info_enum import CodeEnum
from core.exceptions import NotUniqueErrorException

logger = logger_.getLogger(__name__)


class UserRepository:
    def get_user(self, user_id: int) -> Optional[UserEntity]:
        user = session.query(UserModel).filter_by(id=user_id).first()
        if not user:
            return None

        return user.to_entity()

    def create_user(self, dto: CreateUserDto) -> None:
        try:
            user = UserModel(
                id=dto.user_id,
                is_required_agree_terms=dto.is_required_agree_terms,
                join_date=get_server_timestamp().strftime("%Y%m%d"),
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

    def create_device(self, dto: CreateUserDto) -> Optional[int]:
        try:
            device = DeviceModel(
                user_id=dto.user_id,
                uuid=dto.uuid,
                os=dto.os,
                is_active=dto.is_active_device,
                is_auth=dto.is_auth,
                endpoint="",
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

    def create_receive_push_types(self, dto: CreateUserDto) -> None:
        try:
            receive_push_types = ReceivePushTypeModel(user_id=dto.user_id)
            session.add(receive_push_types)
            session.commit()
        except exc.IntegrityError as e:
            logger.error(
                f"[UserRepository][create_receive_push_types] user_id : {dto.user_id} error : {e}"
            )
            session.rollback()
            raise NotUniqueErrorException(type_="T004")

    def update_marketing_receive_push_types(self, dto: CreateAppAgreeTermsDto) -> None:
        try:
            session.query(ReceivePushTypeModel).filter_by(user_id=dto.user_id).update(
                {"is_marketing": False, "updated_at": get_server_timestamp()}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_marketing_receive_push_types] user_id : {dto.user_id} error : {e}"
            )

    def update_user_mobile_auth_info(self, dto: MobileAuthConfirmSmsDto) -> None:
        try:
            session.query(DeviceModel).filter_by(user_id=dto.user_id).update(
                {"phone_number": dto.phone_number, "is_auth": True, "updated_at": get_server_timestamp()}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_mobile_auth_info] user_id : {dto.user_id} error : {e}"
            )

    def create_app_agree_terms(self, dto: CreateAppAgreeTermsDto) -> None:
        try:
            receive_marketing_date = (
                get_server_timestamp() if dto.receive_marketing_yn else None
            )

            user = AppAgreeTermsModel(
                user_id=dto.user_id,
                private_user_info_yn=dto.private_user_info_yn,
                required_terms_yn=dto.required_terms_yn,
                receive_marketing_yn=dto.receive_marketing_yn,
                receive_marketing_date=receive_marketing_date,
            )
            session.add(user)
            session.commit()
        except exc.IntegrityError as e:
            logger.error(
                f"[UserRepository][create_app_agree_terms] user_id : {dto.user_id} error : {e}"
            )
            session.rollback()
            raise NotUniqueErrorException(type_="T005")

    def update_user_required_agree_terms(self, dto: CreateAppAgreeTermsDto) -> None:
        try:
            session.query(UserModel).filter_by(id=dto.user_id).update(
                {"is_required_agree_terms": True, "updated_at": get_server_timestamp()}
            )
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_required_agree_terms] user_id : {dto.user_id} error : {e}"
            )
            raise NotUniqueErrorException(type_="T006")

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

    def create_user_nickname(self, dto: UpsertUserInfoDetailDto) -> int:
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
            raise NotUniqueErrorException(type_="T007")

    def update_user_nickname(self, dto: UpsertUserInfoDetailDto):
        try:
            session.query(UserProfileModel).filter_by(id=dto.user_profile_id).update(
                {"nickname": dto.value, "last_update_code": dto.code, "updated_at": get_server_timestamp()}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_nickname] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def create_user_info(self, dto: UpsertUserInfoDetailDto) -> UserInfoEntity:
        try:
            user_info = UserInfoModel(
                user_profile_id=dto.user_profile_id, code=dto.code, value=dto.value
            )
            session.add(user_info)
            session.commit()

            return user_info.to_entity()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[UserRepository][create_user_info] user_id : {dto.user_id} error : {e}"
            )
            raise NotUniqueErrorException(type_="T008")

    def update_user_info(self, dto: UpsertUserInfoDetailDto) -> UserInfoEntity:
        try:
            user_info_id = session.query(UserInfoModel).filter_by(
                user_profile_id=dto.user_profile_id, code=dto.code
            ).update({"value": dto.value, "updated_at": get_server_timestamp()})
            session.commit()

            return UserInfoEntity(
                id=user_info_id,
                user_profile_id=dto.user_profile_id,
                code=dto.code,
                user_value=dto.value
            )
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_info] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def update_last_code_to_user_info(self, dto: UpsertUserInfoDetailDto) -> None:
        try:
            session.query(UserProfileModel).filter_by(user_id=dto.user_id).update(
                {"last_update_code": dto.code, "updated_at": get_server_timestamp()}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_nickname] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def get_user_info(
            self, dto: GetUserInfoDetailDto
    ) -> Union[UserInfoEntity, UserInfoEmptyEntity]:
        user_info = (
            session.query(UserInfoModel)
                .filter_by(user_profile_id=dto.user_profile_id, code=dto.code)
                .first()
        )

        if not user_info:
            return UserInfoEmptyEntity(code=dto.code)

        return user_info.to_entity()

    def get_user_multi_data_info(
            self, dto: GetUserInfoDto, codes: list
    ) -> Union[UserInfoEntity, UserInfoEmptyEntity]:
        # 복수개의 유저 결과를 리턴할 때
        user_info = (
            session.query(UserInfoModel)
                .filter(UserInfoModel.user_profile_id == dto.user_profile_id,
                        UserInfoModel.code.in_(codes))
                .all()
        )

        if not user_info:
            return UserInfoEmptyEntity(code=dto.code)

        user_values = []
        for query in user_info:
            user_values.append(query.value)

        return UserInfoEntity(id=user_info[0].id, user_profile_id=dto.user_profile_id, code=dto.code,
                              user_values=user_values)

    def get_user_info_by_code(self, user_profile_id: int, code: int) -> Optional[UserInfoEntity]:
        user_info = (
            session.query(UserInfoModel)
                .filter_by(user_profile_id=user_profile_id, code=code)
                .first()
        )
        if not user_info:
            return None

        return user_info.to_entity()

    def get_avg_monthly_income_workers(self) -> AvgMonthlyIncomeWokrerDto:
        result = session.query(AvgMonthlyIncomeWokrerModel).filter_by(is_active=True).first()
        return self._make_avg_monthly_income_worker_object(result)

    def _make_avg_monthly_income_worker_object(self, result: AvgMonthlyIncomeWokrerModel) -> AvgMonthlyIncomeWokrerDto:
        return AvgMonthlyIncomeWokrerDto(
            three=result.three,
            four=result.four,
            five=result.five,
            six=result.six,
            seven=result.seven,
            eight=result.eight
        )

    def get_sido_codes(self, dto: GetUserInfoDetailDto) -> UserInfoCodeValueEntity:
        result = session.query(SidoCodeModel).all()
        return self._make_sido_codes_object(result, dto)

    def _make_sido_codes_object(self, result: List[SidoCodeModel],
                                dto: GetUserInfoDetailDto) -> UserInfoCodeValueEntity:
        code_list = []
        name_list = []

        for data in result:
            if dto.code == CodeEnum.ADDRESS.value:
                code_list.append(data.sido_code)
                name_list.append(data.sido_name)
            else:
                code_list.append(data.sigugun_code)
                name_list.append(data.sigugun_name)

        user_info_code_value_entity = UserInfoCodeValueEntity()
        user_info_code_value_entity.detail_code = code_list
        user_info_code_value_entity.name = name_list

        return user_info_code_value_entity

    def update_user_status_to_out(self, user_id: int) -> None:
        try:
            session.query(UserModel).filter_by(id=user_id).update(
                {"is_out": True, "updated_at": get_server_timestamp()}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_status_to_out] user_id : {user_id} error : {e}"
            )

    def update_app_agree_terms_to_receive_marketing(self, dto: UpdateReceiveNotificationSettingDto) -> None:
        try:
            session.query(AppAgreeTermsModel).filter_by(user_id=dto.user_id).update(
                {"receive_marketing_yn": dto.is_active, "receive_marketing_date": get_server_timestamp(),
                 "updated_at": get_server_timestamp()}
            )
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_app_agree_terms_to_receive_marketing] user_id : {dto.user_id} error : {e}"
            )

    def get_user_survey_step_and_point(self, dto: GetUserDto) -> UserEntity:
        """
        {
            "data": {
                "result":
                    {
                        "survey_step": 0,
                        "point": 1000,
                        "is_badge": true or false,
                    }
            },
            "meta": null
        }
        """
        query = (
            session.query(UserModel).options(
                joinedload(UserModel.user_profile)
            ).options(
                joinedload(UserModel.points)
                    .joinedload(PointModel.point_type)
            ).filter(UserModel.id == dto.user_id)
        )
        user = query.first()
        return user.to_entity()

    def create_recently_view(self, dto: RecentlyViewDto) -> None:
        try:
            view_info = RecentlyViewModel(
                user_id=dto.user_id, house_id=dto.house_id, type=dto.type
            )
            session.add(view_info)
            session.commit()

        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][create_recently_view] user_id : {dto.user_id} house_id: {dto.house_id} error : {e}"
            )

    # def get_recently_view_list(self, dto: GetUserDto):
    #     """
    #         필터 조건 : 분양 매물중
    #     """
    #     filters = list()
    #     filters.append(RecentlyViewModel.user_id == dto.user_id)
    #     filters.append(RecentlyViewModel.type == 1)
    #     filters.append(and_(RealEstateModel.id == RecentlyViewModel.house_id,
    #                         RealEstateModel.is_available == "True",
    #                         PublicSaleModel.real_estate_id == RecentlyViewModel.house_id,
    #                         PublicSaleModel.is_available == "True"))
    #
    #     query = session.query(RecentlyViewModel).filter(*filters).order_by(RecentlyViewModel.created_at).limit(30)
    #
    #     queryset = query.all()