import os
import uuid
from typing import Union, Optional

import inject

from app.extensions.utils.enum.aws_enum import S3PathEnum, S3BucketEnum
from app.extensions.utils.image_helper import S3Helper
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateUserProfileImgDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto,
)
from core.domains.user.entity.user_entity import (
    UserInfoEntity,
    UserInfoCodeValueEntity,
    UserInfoEmptyEntity,
)
from core.domains.user.enum.user_info_enum import (
    IsHouseOwnerCodeEnum,
    IsHouseHolderCodeEnum,
    IsMarriedCodeEnum,
    NumberDependentsEnum,
    IsChildEnum,
    IsSubAccountEnum,
    MonthlyIncomeEnum,
    AssetsRealEstateEnum,
    AssetsCarEnum,
    AssetsTotalEnum,
    SpecialCondEnum,
)
from core.domains.user.repository.user_repository import UserRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class UserBaseUseCase:
    @inject.autoparams()
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def _upload_user_profile_img(self, dto: CreateUserProfileImgDto) -> bool:
        """
             프로필 이미지 등록은 사용 X -> 다만 추후 사용 가능성 있기 때문에 남겨둠
         """
        res = S3Helper.upload(
            bucket=S3BucketEnum.TOADHOME_BUCKET.value,
            file_name=dto.origin_file[0],
            object_name=dto.object_name,
        )

        if not res:
            return None

        return False if not res else True

    def _get_file_split_object(self, dto: CreateUserDto) -> CreateUserProfileImgDto:
        """
             프로필 이미지 등록은 사용 X -> 다만 추후 사용 가능성 있기 때문에 남겨둠
         """
        # file[0] : upload only one file
        f, extension = os.path.splitext(dto.file[0].filename)
        uuid_ = str(uuid.uuid4())
        object_name = S3PathEnum.PROFILE_IMGS.value + uuid_ + extension

        create_user_profile_img_dto = CreateUserProfileImgDto(
            user_id=dto.id,
            uuid_=uuid_,
            file_name=f,
            path=S3PathEnum.PROFILE_IMGS.value,
            extension=extension,
            object_name=object_name,
            origin_file=dto.file,
        )

        return create_user_profile_img_dto


class CreateUserUseCase(UserBaseUseCase):
    def execute(
        self, dto: CreateUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR
            )

        self._user_repo.create_user(dto=dto)

        device_id = self._user_repo.create_device(dto=dto)
        self._user_repo.create_device_token(dto=dto, device_id=device_id)

        # 프로필 이미지 등록은 사용 X -> 다만 추후 사용 가능성 있기 때문에 주석으로 남겨둠
        # if dto.file:
        #     create_user_profile_img_dto = self._get_file_split_object(dto=dto)
        #     """
        #         S3 업로드 실패시에도 로직 실행
        #         가입단계에서 실패처리 시 유저 입장에서는 앱 사용 안할 확률이 높기 때문에
        #     """
        #     if self._upload_user_profile_img(dto=create_user_profile_img_dto):
        #         profile_img_id: Optional[int] = self._user_repo.create_user_profile_img(
        #             dto=create_user_profile_img_dto
        #         )
        #
        #         if profile_img_id:
        #             self._user_repo.update_user_profile_img_id(
        #                 user_id=dto.id, profile_img_id=profile_img_id
        #             )

        return UseCaseSuccessOutput()


class CreateAppAgreeTermsUseCase(UserBaseUseCase):
    def execute(
        self, dto: CreateAppAgreeTermsDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR
            )

        self._user_repo.create_app_agree_terms(dto=dto)
        self._user_repo.update_user_required_agree_terms(dto=dto)

        return UseCaseSuccessOutput()


class UpsertUserInfoUseCase(UserBaseUseCase):
    def execute(
        self, dto: UpsertUserInfoDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR
            )

        user_profile_id: Optional[int] = self._user_repo.get_user_profile_id(dto=dto)

        """
            upsert 사용 X
            클린코드 측면에서 upsert는 되도록 사용 자제 권장한다고 본적이 있어서 제외했지만 이에 따른 코드 복잡성 증가
            코드 컨벤션 논의 필요 -> 논의 후 필요 시 refactoring
        """
        if dto.code == 1000:
            # code==1000 (설문 시작 후 닉네임 생성 시) -> user_profiles 갱신
            if not user_profile_id:
                user_profile_id: int = self._user_repo.create_user_nickname(dto=dto)
            else:
                self._user_repo.update_user_nickname(dto=dto)

        dto.user_profile_id = user_profile_id
        if not self._user_repo.is_user_info(dto=dto):
            self._user_repo.create_user_info(dto=dto)
        else:
            self._user_repo.update_user_info(dto=dto)

        # 마지막으로 진행한 설문 단계 저장
        self._user_repo.update_last_code_to_user_info(dto=dto)

        # todo. SQS Data 전송

        return UseCaseSuccessOutput()


class GetUserInfoUseCase(UserBaseUseCase):
    def execute(
        self, dto: GetUserInfoDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR
            )

        user_profile_id: int = self._user_repo.get_user_profile_id(dto=dto)
        dto.user_profile_id = user_profile_id

        if not dto.user_profile_id:
            # nickname 생성 전 (즉, 최초 설문으로 user_profile_id가 없음)
            user_info: UserInfoEmptyEntity = self._make_empty_user_info_entity(dto=dto)
        else:
            user_info: Union[
                UserInfoEntity, UserInfoEmptyEntity
            ] = self._user_repo.get_user_info(dto=dto)
            self._bind_detail_code_values(user_info=user_info)

        return UseCaseSuccessOutput(value=user_info)

    def _make_empty_user_info_entity(self, dto: GetUserInfoDto) -> UserInfoEmptyEntity:
        return UserInfoEmptyEntity(code=dto.code)

    def _bind_detail_code_values(
        self, user_info: Union[UserInfoEntity, UserInfoEmptyEntity]
    ):
        bind_detail_code_dict = {
            "1005": IsHouseOwnerCodeEnum,
            "1007": IsHouseHolderCodeEnum,
            "1008": IsMarriedCodeEnum,
            "1010": NumberDependentsEnum,
            "1011": IsChildEnum,
            "1015": IsSubAccountEnum,
            "1019": MonthlyIncomeEnum,
            "1020": AssetsRealEstateEnum,
            "1021": AssetsCarEnum,
            "1022": AssetsTotalEnum,
            "1025": SpecialCondEnum,
        }

        bind_code = bind_detail_code_dict.get(str(user_info.code))

        if bind_code:
            user_info_code_value_entity = UserInfoCodeValueEntity()

            user_info_code_value_entity.detail_code = bind_code.COND_CD.value
            user_info_code_value_entity.name = bind_code.COND_NM.value

            user_info.code_values = user_info_code_value_entity
