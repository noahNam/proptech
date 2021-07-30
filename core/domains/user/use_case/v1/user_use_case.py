import os
import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Union, Optional, List

import inject

from app.extensions.queue import SqsTypeEnum, SenderDto
from app.extensions.queue.sender import QueueMessageSender
from app.extensions.utils.enum.aws_enum import S3PathEnum, S3BucketEnum
from app.extensions.utils.event_observer import send_message, get_event_object
from app.extensions.utils.image_helper import S3Helper
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.notification.dto.notification_dto import GetBadgeDto
from core.domains.notification.enum import NotificationTopicEnum
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateUserProfileImgDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto,
    SendUserInfoToLakeDto,
    GetUserDto,
    AvgMonthlyIncomeWokrerDto,
    UpsertUserInfoDetailDto,
)
from core.domains.user.entity.user_entity import (
    UserInfoEntity,
    UserInfoCodeValueEntity,
    UserEntity,
    UserProfileEntity,
    UserInfoResultEntity,
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
    SpecialCondEnum,
    CodeEnum,
    AddressCodeEnum,
    AddressDetailCodeEnum,
    CodeStepEnum,
    IsSupportParentCodeEnum,
)
from core.domains.user.repository.user_repository import UserRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class UserBaseUseCase:
    @inject.autoparams()
    def __init__(self, user_repo: UserRepository, queue_msg_sender: QueueMessageSender):
        self._user_repo = user_repo
        self._sqs = queue_msg_sender

    def _send_sqs_message(self, queue_type: SqsTypeEnum, msg: SenderDto) -> bool:
        return self._sqs.send_message(queue_type=queue_type, msg=msg, logging=True)

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
    def execute(
        self, dto: GetUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        user: UserEntity = self._user_repo.get_user(user_id=dto.user_id)

        return UseCaseSuccessOutput(value=user)


class CreateUserUseCase(UserBaseUseCase):
    def execute(
        self, dto: CreateUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        self._user_repo.create_user(dto=dto)

        device_id = self._user_repo.create_device(dto=dto)
        self._user_repo.create_device_token(dto=dto, device_id=device_id)

        self._user_repo.create_receive_push_types(dto=dto)

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
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        self._user_repo.create_app_agree_terms(dto=dto)
        self._user_repo.update_user_required_agree_terms(dto=dto)

        if not dto.receive_marketing_yn:
            self._user_repo.update_marketing_receive_push_types(dto=dto)

        return UseCaseSuccessOutput()


class UpsertUserInfoUseCase(UserBaseUseCase):
    def execute(
        self, dto: UpsertUserInfoDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        user_profile_id: Optional[int] = self._user_repo.get_user_profile_id(dto=dto)

        """
            upsert 사용 X
            클린코드 측면에서 upsert는 되도록 사용 자제 권장한다고 본적이 있어서 제외했지만 이에 따른 코드 복잡성 증가
            코드 컨벤션 논의 필요 -> 논의 후 필요 시 refactoring
        """
        for idx in range(len(dto.codes)):
            detail_dto = UpsertUserInfoDetailDto(
                user_id=dto.user_id,
                user_profile_id=user_profile_id,
                code=dto.codes[idx],
                value=dto.values[idx] if dto.values else None,
            )

            if detail_dto.code == CodeEnum.NICKNAME.value:
                # code==1000 (설문 시작 후 닉네임 생성 시) -> user_profiles 갱신
                if not user_profile_id:
                    user_profile_id: int = self._user_repo.create_user_nickname(
                        dto=detail_dto
                    )
                else:
                    self._user_repo.update_user_nickname(dto=detail_dto)

            detail_dto.user_profile_id = user_profile_id
            if not self._user_repo.is_user_info(dto=detail_dto):
                user_info: UserInfoResultEntity = self._user_repo.create_user_info(
                    dto=detail_dto
                )
            else:
                user_info: UserInfoResultEntity = self._user_repo.update_user_info(
                    dto=detail_dto
                )

            # 마지막으로 진행한 설문 단계 저장
            self._user_repo.update_last_code_to_user_info(dto=detail_dto)

            # SQS Data 전송 -> Data Lake
            if user_info.user_value:
                msg: SenderDto = self._make_sqs_send_message(dto=detail_dto)
                self._send_sqs_message(
                    queue_type=SqsTypeEnum.USER_DATA_SYNC_TO_LAKE, msg=msg
                )

        return UseCaseSuccessOutput()

    def _make_sqs_send_message(self, dto: UpsertUserInfoDetailDto) -> SenderDto:
        send_user_info_to_lake_dto = SendUserInfoToLakeDto(
            user_id=dto.user_id,
            user_profile_id=dto.user_profile_id,
            code=dto.code,
            value=dto.value,
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
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        user_profile_id: Optional[int] = self._user_repo.get_user_profile_id(dto=dto)
        dto.user_profile_id = user_profile_id

        user_info_entity: List[
            UserInfoEntity
        ] = self._user_repo.get_user_multi_data_info(dto=dto)

        # 유저 설문이 작성되지 않은 object 생성
        self._make_empty_object(user_infos=user_info_entity, dto=dto)
        user_info_result_entity: List[
            UserInfoResultEntity
        ] = self._bind_detail_code_values(user_infos=user_info_entity)

        return UseCaseSuccessOutput(value=user_info_result_entity)

    def _make_empty_object(
        self, user_infos: List[UserInfoEntity], dto: GetUserInfoDto
    ) -> None:
        if dto.survey_step == 1:
            # 1단계 설문 데이터 조회
            survey_step_codes = CodeStepEnum.ONE.value
        else:
            # 2단계 설문 데이터 조회
            survey_step_codes = CodeStepEnum.TWO.value

        user_info_codes = [user_info.code for user_info in user_infos]
        empty_codes: list = list(set(survey_step_codes) - set(user_info_codes))

        empty_user_info_entity = [
            UserInfoEntity(
                user_profile_id=dto.user_profile_id, code=empty_code, value=None,
            )
            for empty_code in empty_codes
        ]

        user_infos.extend(empty_user_info_entity)

    def _bind_detail_code_values(
        self, user_infos: List[UserInfoEntity],
    ) -> List[UserInfoResultEntity]:
        results = list()
        for user_info in user_infos:
            user_info_result_entity = UserInfoResultEntity(
                code=user_info.code, code_values=None, user_value=user_info.value
            )

            bind_detail_code_dict = {
                "1002": AddressCodeEnum,
                "1003": AddressDetailCodeEnum,
                "1005": IsHouseOwnerCodeEnum,
                "1007": IsHouseHolderCodeEnum,
                "1008": IsMarriedCodeEnum,
                "1010": NumberDependentsEnum,
                "1011": IsChildEnum,
                "1016": IsSubAccountEnum,
                "1020": MonthlyIncomeEnum,
                "1021": AssetsRealEstateEnum,
                "1022": AssetsCarEnum,
                "1023": AssetsTotalEnum,
                "1024": IsSupportParentCodeEnum,
                "1026": SpecialCondEnum,
            }

            bind_code = bind_detail_code_dict.get(str(user_info.code))

            if not bind_code:
                results.append(user_info_result_entity)
                continue

            if bind_code == AddressCodeEnum or bind_code == AddressDetailCodeEnum:
                user_info_code_value_entity: UserInfoCodeValueEntity = self._user_repo.get_sido_codes(
                    code=user_info.code
                )
                user_info_result_entity.code_values = user_info_code_value_entity
                results.append(user_info_result_entity)

            elif bind_code == MonthlyIncomeEnum:
                # 외벌이, 맞벌이 확인
                # 외벌이 -> 1,3,4 / 맞벌이 -> 2
                is_married_result: UserInfoEntity = UserRepository().get_user_info_by_code(
                    user_profile_id=user_info.user_profile_id,
                    code=CodeEnum.IS_MARRIED.value,
                )

                # 부양가족 수
                # 3인 이하->1,2,3,9(0명) / 4인->4 / 5인->5 / 6인->6 / 7인->7 / 8명 이상->8
                number_dependents_result: UserInfoEntity = UserRepository().get_user_info_by_code(
                    user_profile_id=user_info.user_profile_id,
                    code=CodeEnum.NUMBER_DEPENDENTS.value,
                )

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
                    "9": income_result.three,  # 0명
                }

                calc_result_list = []

                if number_dependents_result:
                    my_basic_income = income_result_dict.get(
                        number_dependents_result.value
                    )
                    monthly_income_enum: List = MonthlyIncomeEnum.COND_CD_1.value if is_married_result.value != "2" else MonthlyIncomeEnum.COND_CD_2.value
                else:
                    # 설문 1단계를 완료 안하고 들어오지 못하지만 가드 코드 추가
                    # my_basic_income = 부양가족 3인 기본 값
                    # monthly_income_enum = 외벌이 기준
                    my_basic_income = income_result_dict.get("1")
                    monthly_income_enum: List = MonthlyIncomeEnum.COND_CD_1.value

                for percentage_num in monthly_income_enum:
                    income_by_segment = (int(my_basic_income) * percentage_num) / 100
                    income_by_segment = round(income_by_segment)
                    calc_result_list.append(income_by_segment)

                user_info_code_value_entity = UserInfoCodeValueEntity()

                user_info_code_value_entity.detail_code = monthly_income_enum
                user_info_code_value_entity.name = calc_result_list

                user_info_result_entity.code_values = user_info_code_value_entity
                results.append(user_info_result_entity)
            else:
                user_info_code_value_entity = UserInfoCodeValueEntity()

                user_info_code_value_entity.detail_code = bind_code.COND_CD.value
                user_info_code_value_entity.name = bind_code.COND_NM.value

                user_info_result_entity.code_values = user_info_code_value_entity
                results.append(user_info_result_entity)

        return results


class UserOutUseCase(UserBaseUseCase):
    def execute(
        self, dto: GetUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        self._user_repo.update_user_status_to_out(user_id=dto.user_id)

        return UseCaseSuccessOutput()


class GetUserMainUseCase(UserBaseUseCase):
    def execute(
        self, dto: GetUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        """
        ticket은 tickets 스키마의 sum(amount)로 가져온다. -> 안정성을 위해
        즉, user 스키마의 number_ticket은 현재로서는 사용안하고, 티켓의 변화가 있을 때 업데이트 용도로만 사용한다.
        추후에, 사용자가 많아지고 ticket 합산으로 인한 퍼포먼스 문제가 발생할 시에 user.number_ticket에서 가져오는 것으로 수정 한다.
        그 전까지는 sum(tickets.amount) == user.number_ticket 이 맞는지 꾸준히 확인하여 로직이 세는 곳이 있는지 트래킹한다.
        """

        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # survey_step(설문 단계) + ticket 조회
        user: UserEntity = self._user_repo.get_user_survey_step_and_ticket(dto=dto)

        # badge 여부 조회
        is_badge: bool = self._get_badge(dto=dto)
        result: dict = self._make_result_object(user=user, is_badge=is_badge)

        return UseCaseSuccessOutput(value=result)

    def _make_result_object(self, user: UserEntity, is_badge: bool):
        return dict(
            survey_step=user.survey_step, tickets=user.total_amount, is_badge=is_badge
        )

    def _get_badge(self, dto: GetUserDto) -> bool:
        dto = GetBadgeDto(user_id=dto.user_id)
        send_message(topic_name=NotificationTopicEnum.GET_BADGE, dto=dto)
        return get_event_object(topic_name=NotificationTopicEnum.GET_BADGE)


class GetSurveyResultUseCase(UserBaseUseCase):
    def execute(
        self, dto: GetUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        user_profile_entity: Optional[
            UserProfileEntity
        ] = self._user_repo.get_survey_result(dto=dto)

        if not user_profile_entity:
            return UseCaseFailureOutput(
                type="survey_result",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        if not user_profile_entity.user_infos:
            return UseCaseFailureOutput(
                type="wrong_survey_step",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        age: int = self._calc_age(user_profile_entity=user_profile_entity)
        return UseCaseSuccessOutput(
            value=dict(age=age, user_profile_entity=user_profile_entity)
        )

    def _calc_age(self, user_profile_entity: UserProfileEntity) -> int:
        # 생일로 나이 계산
        birth = user_profile_entity.user_infos[0].user_value
        birth = datetime.strptime(birth, "%Y%m%d")
        today = get_server_timestamp()

        return today.year - birth.year
