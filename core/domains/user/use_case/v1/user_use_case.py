import os
import uuid
from typing import Union, Optional, List

import inject

from app.extensions.utils.enum.aws_enum import S3PathEnum, S3BucketEnum
from app.extensions.utils.image_helper import S3Helper
from core.domains.user.dto.user_dto import CreateUserDto, CreateUserProfileImgDto
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
            bucket=S3BucketEnum.APARTALK_BUCKET.value,
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
        self._user_repo.create_interest_regions(dto=dto)
        self._user_repo.update_interest_region_group_counts(dto=dto)

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
