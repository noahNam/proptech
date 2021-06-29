import os
import uuid
from http import HTTPStatus
from typing import Union, Optional, List

import inject

from app.extensions.queue import SqsTypeEnum, SenderDto
from app.extensions.queue.sender import QueueMessageSender
from app.extensions.utils.enum.aws_enum import S3PathEnum, S3BucketEnum
from app.extensions.utils.image_helper import S3Helper
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateUserProfileImgDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto, SendUserInfoToLakeDto, GetUserDto, AvgMonthlyIncomeWokrerDto,
)
from core.domains.user.entity.user_entity import (
    UserInfoEntity,
    UserInfoCodeValueEntity,
    UserInfoEmptyEntity, UserEntity,
)
from core.domains.user.enum.user_enum import UserSqsTypeEnum
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
    SpecialCondEnum, CodeEnum, AddressCodeEnum,
)
from core.domains.user.repository.user_repository import UserRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class UserBaseUseCase:
    @inject.autoparams()
    def __init__(self, user_repo: UserRepository, queue_msg_sender: QueueMessageSender):
        self._user_repo = user_repo
        self._sqs = queue_msg_sender

    def _send_sqs_message(self, queue_type: SqsTypeEnum, msg: SenderDto) -> bool:
        return self._sqs.send_message(
            queue_type=queue_type, msg=msg, logging=True
        )

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


class GetUserUseCase(UserBaseUseCase):
    def execute(self, dto: GetUserDto) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        user: UserEntity = self._user_repo.get_user(user_id=dto.user_id)

        if not user:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
            )

        return UseCaseSuccessOutput(value=user)


class CreateUserUseCase(UserBaseUseCase):
    def execute(
            self, dto: CreateUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
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
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
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
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
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
            user_info: UserInfoEntity = self._user_repo.create_user_info(dto=dto)
        else:
            user_info: UserInfoEntity = self._user_repo.update_user_info(dto=dto)

        # 마지막으로 진행한 설문 단계 저장
        self._user_repo.update_last_code_to_user_info(dto=dto)

        # SQS Data 전송 -> Data Lake
        if user_info.user_value:
            msg: SenderDto = self._make_sqs_send_message(user_info=user_info, user_id=dto.user_id)
            self._send_sqs_message(queue_type=SqsTypeEnum.USER_DATA_SYNC_TO_LAKE, msg=msg)

        return UseCaseSuccessOutput()

    def _make_sqs_send_message(self, user_info: UserInfoEntity, user_id: int) -> SenderDto:
        send_user_info_to_lake_dto = SendUserInfoToLakeDto(
            user_id=user_id,
            user_profile_id=user_info.user_profile_id,
            code=user_info.code,
            value=user_info.user_value,
        )

        return SenderDto(
            msg_type=UserSqsTypeEnum.SEND_USER_DATA_TO_LAKE.value,
            msg=send_user_info_to_lake_dto.to_dict(),
            msg_created_at=get_server_timestamp().strftime("%Y/%m/%d, %H:%M:%S"),
        )


class GetUserInfoUseCase(UserBaseUseCase):
    def execute(
            self, dto: GetUserInfoDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id", message=FailureType.NOT_FOUND_ERROR, code=HTTPStatus.NOT_FOUND
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

            if not user_info.user_profile_id:
                user_info.user_profile_id = user_profile_id
                self._bind_detail_code_values(user_info=user_info)

        return UseCaseSuccessOutput(value=user_info)

    def _make_empty_user_info_entity(self, dto: GetUserInfoDto) -> UserInfoEmptyEntity:
        return UserInfoEmptyEntity(code=dto.code)

    def _bind_detail_code_values(
            self, user_info: Union[UserInfoEntity, UserInfoEmptyEntity]
    ):
        bind_detail_code_dict = {
            "1002": AddressCodeEnum,
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

        if not bind_code:
            return

        if bind_code != MonthlyIncomeEnum and bind_code != MonthlyIncomeEnum:
            user_info_code_value_entity = UserInfoCodeValueEntity()

            user_info_code_value_entity.detail_code = bind_code.COND_CD.value
            user_info_code_value_entity.name = bind_code.COND_NM.value

            user_info.code_values = user_info_code_value_entity
        else:
            # 외벌이, 맞벌이 확인
            # 외벌이 -> 1,3,4 / 맞벌이 -> 2
            result1: UserInfoEntity = UserRepository().get_user_info_by_code(user_profile_id=user_info.user_profile_id,
                                                                             code=CodeEnum.IS_MARRIED.value)

            # 부양가족 수
            # 3인 이하->1,2,3,9 / 4인->4 / 5인->5 / 6인->6 / 7인->7 / 8명 이상->8
            result2: UserInfoEntity = UserRepository().get_user_info_by_code(user_profile_id=user_info.user_profile_id,
                                                                             code=CodeEnum.NUMBER_DEPENDENTS.value)

            # 부양가족별 basic 소득
            income_result: AvgMonthlyIncomeWokrerDto = UserRepository().get_avg_monthly_income_workers()
            income_result_dict = {
                "1": income_result.three,
                "2": income_result.three,
                "3": income_result.three,
                "4": income_result.four,
                "5": income_result.five,
                "6": income_result.six,
                "7": income_result.seven,
                "8": income_result.eight,
                "9": income_result.three,
            }

            calc_result_list = []
            my_basic_income = income_result_dict.get(result2.user_value)

            monthly_income_enum: List = MonthlyIncomeEnum.COND_CD_1.value if result1.user_value != "2" else MonthlyIncomeEnum.COND_CD_2.value

            for percentage_num in monthly_income_enum:
                income_by_segment = (int(my_basic_income) * percentage_num) / 100
                income_by_segment = round(income_by_segment)
                calc_result_list.append(income_by_segment)

            user_info_code_value_entity = UserInfoCodeValueEntity()

            user_info_code_value_entity.detail_code = monthly_income_enum
            user_info_code_value_entity.name = calc_result_list

            user_info.code_values = user_info_code_value_entity
