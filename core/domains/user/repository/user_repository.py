from typing import Optional, List

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
    UserModel,
    RecentlyViewModel,
)
from core.domains.notification.dto.notification_dto import (
    UpdateReceiveNotificationSettingDto,
)
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateAppAgreeTermsDto,
    GetUserInfoDto,
    AvgMonthlyIncomeWokrerDto,
    UpsertUserInfoDetailDto,
    GetUserDto,
    RecentlyViewDto,
)
from core.domains.user.entity.user_entity import (
    UserInfoEntity,
    UserEntity,
    UserInfoCodeValueEntity,
    UserProfileEntity,
    SidoCodeEntity,
)
from core.domains.user.enum.user_info_enum import CodeEnum, CodeStepEnum
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
                email=dto.email,
                is_required_agree_terms=dto.is_required_agree_terms,
                join_date=get_server_timestamp().strftime("%Y%m%d"),
                is_active=dto.is_active,
                is_out=dto.is_out,
                created_at=get_server_timestamp(),
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
                phone_number=dto.phone_number,
                uuid=dto.uuid,
                os=dto.os,
                is_active=dto.is_active_device,
                is_auth=dto.is_auth,
                endpoint="",
                created_at=get_server_timestamp(),
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
            device_token = DeviceTokenModel(device_id=device_id, token=dto.token,)
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
                created_at=get_server_timestamp(),
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

    def get_user_profile(self, user_id: int) -> Optional[UserProfileEntity]:
        user_profile = (
            session.query(UserProfileModel).filter_by(user_id=user_id).first()
        )
        if not user_profile:
            return None

        return user_profile.to_entity()

    def is_user_info(self, dto: UpsertUserInfoDetailDto) -> bool:
        return session.query(
            exists()
            .where(UserInfoModel.user_profile_id == dto.user_profile_id)
            .where(UserInfoModel.code == dto.code)
        ).scalar()

    def is_surveys_complete(self, dto: UpsertUserInfoDetailDto) -> bool:
        return session.query(
            exists()
            .where(UserInfoModel.user_profile_id == dto.user_profile_id)
            .where(UserInfoModel.code == CodeEnum.SPECIAL_COND.value)
        ).scalar()

    def create_user_nickname(self, dto: UpsertUserInfoDetailDto) -> int:
        try:
            user_profile = UserProfileModel(
                user_id=dto.user_id, nickname=dto.value, last_update_code=dto.code, created_at=get_server_timestamp(),
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

    def update_user_nickname(self, dto: UpsertUserInfoDetailDto) -> None:
        try:
            session.query(UserProfileModel).filter_by(id=dto.user_profile_id).update(
                {
                    "nickname": dto.value,
                    "last_update_code": dto.code,
                    "updated_at": get_server_timestamp(),
                }
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_nickname] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def create_user_info(self, dto: UpsertUserInfoDetailDto) -> None:
        try:
            user_info = UserInfoModel(
                user_profile_id=dto.user_profile_id, code=dto.code, value=dto.value, created_at=get_server_timestamp(),
            )
            session.add(user_info)
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[UserRepository][create_user_info] user_id : {dto.user_id} error : {e}"
            )
            raise NotUniqueErrorException(type_="T008")

    def update_user_info(self, dto: UpsertUserInfoDetailDto) -> None:
        try:
            session.query(UserInfoModel).filter_by(
                user_profile_id=dto.user_profile_id, code=dto.code
            ).update({"value": dto.value, "updated_at": get_server_timestamp()})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_info] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def update_chain_user_info(self, user_profile_id: int, codes: list) -> None:
        try:
            session.query(UserInfoModel).filter(
                UserInfoModel.user_profile_id == user_profile_id,
                UserInfoModel.code.in_(codes),
            ).update({"value": None, "updated_at": get_server_timestamp()})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_chain_user_info] user_profile_id : {user_profile_id} error : {e}"
            )
            raise Exception

    def update_last_code_to_user_info(
        self, dto: UpsertUserInfoDetailDto, survey_step: Optional[int]
    ) -> None:
        try:
            update_variable = dict()
            update_variable["last_update_code"] = dto.code
            update_variable["updated_at"] = get_server_timestamp()
            if survey_step:
                update_variable["survey_step"] = survey_step

            session.query(UserProfileModel).filter_by(user_id=dto.user_id).update(
                update_variable
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_last_code_to_user_info] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def get_user_multi_data_info(self, dto: GetUserInfoDto) -> List[UserInfoEntity]:
        filters = list()
        filters.append(UserInfoModel.user_profile_id == dto.user_profile_id)

        if dto.survey_step == 1:
            # 1단계 설문 데이터 조회
            filters.append(UserInfoModel.code.in_(CodeStepEnum.ONE.value))
        else:
            # 2단계 설문 데이터 조회
            filters.append(UserInfoModel.code.in_(CodeStepEnum.TWO.value))

        user_infos = session.query(UserInfoModel).filter(*filters).all()

        if not user_infos:
            return []

        return [
            UserInfoEntity(
                user_profile_id=user_info.user_profile_id,
                code=user_info.code,
                value=user_info.value,
            )
            for user_info in user_infos
        ]

    def get_user_info_by_code(
        self, user_profile_id: int, code: int
    ) -> Optional[UserInfoEntity]:
        user_info = (
            session.query(UserInfoModel)
            .filter_by(user_profile_id=user_profile_id, code=code)
            .first()
        )
        if not user_info:
            return None

        return user_info.to_entity()

    def get_avg_monthly_income_workers(self) -> AvgMonthlyIncomeWokrerDto:
        result = (
            session.query(AvgMonthlyIncomeWokrerModel).filter_by(is_active=True).first()
        )
        return self._make_avg_monthly_income_worker_object(result)

    def _make_avg_monthly_income_worker_object(
        self, result: AvgMonthlyIncomeWokrerModel
    ) -> AvgMonthlyIncomeWokrerDto:
        return AvgMonthlyIncomeWokrerDto(
            three=result.three,
            four=result.four,
            five=result.five,
            six=result.six,
            seven=result.seven,
            eight=result.eight,
        )

    def get_sido_codes(self, code: int) -> UserInfoCodeValueEntity:
        result = session.query(SidoCodeModel).all()
        return self._make_sido_codes_object(result, code)

    def _make_sido_codes_object(
        self, result: List[SidoCodeModel], code: int
    ) -> UserInfoCodeValueEntity:
        code_list = []
        name_list = []

        for data in result:
            if code == CodeEnum.ADDRESS.value:
                code_list.append(data.sido_code)
                name_list.append(data.sido_name)
            else:
                code_list.append(data.sigugun_code)
                name_list.append(data.sigugun_name)

        user_info_code_value_entity = UserInfoCodeValueEntity()
        user_info_code_value_entity.detail_code = code_list
        user_info_code_value_entity.name = name_list

        return user_info_code_value_entity

    def get_sido_name(self, sido_id: int, sigugun_id: int) -> SidoCodeEntity:
        query_set = (
            session.query(SidoCodeModel)
            .filter_by(sido_code=sido_id, sigugun_code=sigugun_id)
            .first()
        )
        return query_set.to_entity()

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

    def update_app_agree_terms_to_receive_marketing(
        self, dto: UpdateReceiveNotificationSettingDto
    ) -> None:
        try:
            session.query(AppAgreeTermsModel).filter_by(user_id=dto.user_id).update(
                {
                    "receive_marketing_yn": dto.is_active,
                    "receive_marketing_date": get_server_timestamp(),
                    "updated_at": get_server_timestamp(),
                }
            )
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_app_agree_terms_to_receive_marketing] user_id : {dto.user_id} error : {e}"
            )

    def get_user_survey_step_and_ticket(self, dto: GetUserDto) -> UserEntity:
        query = (
            session.query(UserModel)
            .options(joinedload(UserModel.user_profile))
            .options(joinedload(UserModel.tickets))
            .filter(UserModel.id == dto.user_id)
        )
        user = query.first()
        return user.to_entity()

    def create_recently_view(self, dto: RecentlyViewDto) -> None:
        try:
            view_info = RecentlyViewModel(
                user_id=dto.user_id, house_id=dto.house_id, type=dto.type, created_at=get_server_timestamp(),
            )
            session.add(view_info)
            session.commit()

        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][create_recently_view] user_id : {dto.user_id} house_id: {dto.house_id} error : {e}"
            )

    def update_user_nickname_of_profile_setting(
        self, dto: UpsertUserInfoDetailDto
    ) -> None:
        try:
            session.query(UserProfileModel).filter_by(id=dto.user_profile_id).update(
                {
                    "nickname": dto.value,
                    "last_update_code": dto.code,
                    "updated_at": get_server_timestamp(),
                }
            )
            session.query(UserInfoModel).filter_by(
                user_profile_id=dto.user_profile_id, code=dto.code
            ).update({"value": dto.value, "updated_at": get_server_timestamp()})

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[UserRepository][update_user_nickname_of_profile_setting] user_id : {dto.user_id} error : {e}"
            )
            raise Exception

    def is_duplicate_nickname(self, nickname: str) -> bool:
        return session.query(
            session.query(UserProfileModel).filter_by(nickname=nickname).exists()
        ).scalar()
