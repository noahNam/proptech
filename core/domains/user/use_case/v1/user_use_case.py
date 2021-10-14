import os
import uuid
from http import HTTPStatus
from typing import Union, Optional, List

import inject
import requests

from app.extensions.queue import SqsTypeEnum, SenderDto
from app.extensions.queue.sender import QueueMessageSender
from app.extensions.utils.enum.aws_enum import S3PathEnum, S3BucketEnum
from app.extensions.utils.event_observer import send_message, get_event_object
from app.extensions.utils.image_helper import S3Helper
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.notification.dto.notification_dto import GetBadgeDto
from core.domains.notification.enum import NotificationTopicEnum
from core.domains.payment.enum import PaymentTopicEnum
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
    UpdateUserProfileDto,
    GetUserProviderDto,
)
from core.domains.user.entity.user_entity import (
    UserInfoEntity,
    UserInfoCodeValueEntity,
    UserEntity,
    UserProfileEntity,
    UserInfoResultEntity,
    SidoCodeEntity,
)
from core.domains.user.enum.user_enum import (
    UserSqsTypeEnum,
    UserSurveyStepEnum,
    UserProviderCallEnum,
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
    CodeEnum,
    AddressCodeEnum,
    AddressDetailCodeEnum,
    CodeStepEnum,
    IsSupportParentCodeEnum,
)
from core.domains.user.repository.user_repository import UserRepository
from core.domains.user.schema.user_schema import (
    GetSurveysBaseSchema,
    GetUserProviderBaseSchema,
)
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class UserBaseUseCase:
    @inject.autoparams()
    def __init__(self, user_repo: UserRepository, queue_msg_sender: QueueMessageSender):
        self._user_repo = user_repo
        self._sqs = queue_msg_sender

    def _send_sqs_message(self, queue_type: SqsTypeEnum, msg: SenderDto) -> bool:
        return self._sqs.send_message(queue_type=queue_type, msg=msg, logging=True)

    def _check_nickname_for_duplicate(self, nickname: str) -> bool:
        return self._user_repo.is_duplicate_nickname(nickname=nickname)

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

        if dto.codes[
            0
        ] == CodeEnum.NICKNAME.value and self._check_nickname_for_duplicate(
            nickname=dto.values[0]
        ):
            return UseCaseFailureOutput(
                type="duplicate nickname",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )

        user_profile: Optional[UserProfileEntity] = self._user_repo.get_user_profile(
            user_id=dto.user_id
        )

        """
            upsert 사용 X
            클린코드 측면에서 upsert는 되도록 사용 자제 권장한다고 본적이 있어서 제외했지만 이에 따른 코드 복잡성 증가
            코드 컨벤션 논의 필요 -> 논의 후 필요 시 refactoring
        """
        for idx in range(len(dto.codes)):
            detail_dto = UpsertUserInfoDetailDto(
                user_id=dto.user_id,
                user_profile_id=user_profile.id if user_profile else None,
                code=dto.codes[idx],
                value=dto.values[idx] if dto.values else None,
            )

            if detail_dto.code == CodeEnum.NICKNAME.value:
                # code==1000 (설문 시작 후 닉네임 생성 시) -> user_profiles 갱신
                if not user_profile:
                    user_profile_id: int = self._user_repo.create_user_nickname(
                        dto=detail_dto
                    )
                    detail_dto.user_profile_id = user_profile_id
                else:
                    self._user_repo.update_user_nickname(dto=detail_dto)

            chain_codes = list()

            if not self._user_repo.is_user_info(dto=detail_dto):
                self._user_repo.create_user_info(dto=detail_dto)
            else:
                self._user_repo.update_user_info(dto=detail_dto)

                # chain update (하위 질문 초기화)
                chain_codes: List[int] = self._make_chain_update_user_info(
                    dto=detail_dto
                )
                if chain_codes:
                    self._user_repo.update_chain_user_info(
                        user_profile_id=detail_dto.user_profile_id, codes=chain_codes
                    )

            # 설문 단계 조회
            survey_step: Optional[int] = self._get_survey_step(
                dto=detail_dto, user_profile=user_profile
            )

            # 마지막으로 진행한 설문 질문 저장
            self._user_repo.update_last_code_to_user_info(
                dto=detail_dto, survey_step=survey_step
            )

            # 설문 완료 시 무료 티켓 추가 (이미 무료 티켓을 받았으면 추가 발급 X)
            if survey_step == UserSurveyStepEnum.STEP_COMPLETE.value:
                self._create_join_ticket(dto=detail_dto)

            # SQS Data 전송 -> Data Lake
            # 닉네임일 때는 제외
            if detail_dto.value and detail_dto.code != CodeEnum.NICKNAME.value:
                msg: SenderDto = self._make_sqs_send_message(
                    dto=detail_dto, survey_step=survey_step
                )
                self._send_sqs_message(
                    queue_type=SqsTypeEnum.USER_DATA_SYNC_TO_LAKE, msg=msg
                )

            if chain_codes:
                for code in chain_codes:
                    # chain update (하위 질문 초기화)
                    detail_dto.code = code
                    detail_dto.value = None

                    msg: SenderDto = self._make_sqs_send_message(
                        dto=detail_dto, survey_step=survey_step
                    )
                    self._send_sqs_message(
                        queue_type=SqsTypeEnum.USER_DATA_SYNC_TO_LAKE, msg=msg
                    )

        return UseCaseSuccessOutput()

    def _create_join_ticket(self, dto: UpsertUserInfoDetailDto) -> None:
        send_message(
            topic_name=PaymentTopicEnum.CREATE_JOIN_TICKET, user_id=dto.user_id
        )
        return get_event_object(topic_name=PaymentTopicEnum.CREATE_JOIN_TICKET)

    def _get_survey_step(
        self, dto: UpsertUserInfoDetailDto, user_profile: Optional[UserProfileEntity]
    ) -> Optional[int]:
        """
            ** 큰 틀은 2단계 설문 진행중이 유저가 1단계 설문의 어떤 질문을 재 수정하더라도 survey_step은 최종단계를 유지. 즉, 작아질 수는 없다.
            1. get_user_profile -> survey_step 가져옴
            2. survey_step이 null 이면 설문작성을 이제 시작했으므로 UserSurveyStepEnum.STEP_ONE(1 단계 진행중)로 변경

            3. survey_step이 1이고, dto.code가 1016, dto.value가 2(없어요)이면 UserSurveyStepEnum.STEP_TWO(2 단계 진행중)로 변경
            4. survey_step이 1이고, dto.code가 1016, dto.value가 1(있어요)이면 UserSurveyStepEnum.STEP_ONE(1 단계 진행중)을 유지
            5. survey_step이 1이고, dto.code가 1019 이면 UserSurveyStepEnum.STEP_TWO(2 단계 진행중)로 변경

            6. survey_step가 2이고 dto.code가 1026이면 설문 완료
            7. survey_step이 이미 설문완료이면 변화 없음
        """
        if not user_profile:
            return UserSurveyStepEnum.STEP_ONE.value

        survey_step = user_profile.survey_step

        if survey_step == UserSurveyStepEnum.STEP_ONE.value:
            # survey_step이 1이고, dto.code가 1016, dto.value가 2(없어요)이면 UserSurveyStepEnum.STEP_TWO(2 단계 진행중)로 변경
            if dto.code == CodeEnum.IS_SUB_ACCOUNT.value and dto.value == "2":
                return UserSurveyStepEnum.STEP_TWO.value

            # survey_step이 1이고, dto.code가 1019 이면 UserSurveyStepEnum.STEP_TWO(2 단계 진행중)로 변경
            if dto.code == CodeEnum.SUB_ACCOUNT_TOTAL_PRICE.value:
                return UserSurveyStepEnum.STEP_TWO.value

        elif survey_step == UserSurveyStepEnum.STEP_TWO.value:
            # survey_step가 2이고 dto.code가 1026이면 설문 완료
            if self._user_repo.is_surveys_complete(dto=dto):
                return UserSurveyStepEnum.STEP_COMPLETE.value

        return survey_step

    def _make_chain_update_user_info(
        self, dto: UpsertUserInfoDetailDto
    ) -> Optional[List[int]]:
        chain_parent = [
            CodeEnum.IS_HOUSE_OWNER.value,
            CodeEnum.IS_MARRIED.value,
            CodeEnum.IS_CHILD.value,
            CodeEnum.IS_SUB_ACCOUNT.value,
            CodeEnum.IS_SUPPORT_PARENT.value,
        ]
        if dto.code not in chain_parent:
            return None

        update_value_dict = {
            "1005": ["1", "2"],  # "있어요", "없어요", "과거에 있었지만 현재는 처분했어요"
            "1008": ["3", "4"],  # "기혼(외벌이)", "기혼(맞벌이)", "미혼", "한부모"
            "1011": ["4"],  # "자녀 1명", "자녀 2명", "자녀 3명 이상", "없어요"
            "1016": ["2"],  # "있어요", "없어요"
            "1024": ["2"],  # "예", "아니요"
        }
        update_value_bind_code = update_value_dict.get(str(dto.code))
        if dto.value not in update_value_bind_code:
            return None

        chain_child_dict = {
            "1005": [CodeEnum.SELL_HOUSE_DATE.value],
            "1008": [CodeEnum.MARRIAGE_REG_DATE.value],
            "1011": [
                CodeEnum.CHILD_AGE_SIX.value,
                CodeEnum.CHILD_AGE_NINETEEN.value,
                CodeEnum.CHILD_AGE_TWENTY.value,
                CodeEnum.MOST_CHILD_YOUNG_AGE.value,
            ],
            "1016": [
                CodeEnum.SUB_ACCOUNT_DATE.value,
                CodeEnum.SUB_ACCOUNT_TIMES.value,
                CodeEnum.SUB_ACCOUNT_TOTAL_PRICE.value,
            ],
            "1024": [CodeEnum.SUPPORT_PARENT_DATE.value],
        }

        codes = chain_child_dict.get(str(dto.code))

        return codes

    def _make_sqs_send_message(
        self, dto: UpsertUserInfoDetailDto, survey_step
    ) -> SenderDto:
        send_user_info_to_lake_dto = SendUserInfoToLakeDto(
            user_id=dto.user_id,
            user_profile_id=dto.user_profile_id,
            code=dto.code,
            value=dto.value,
            survey_step=survey_step,
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

        user_profile: Optional[UserProfileEntity] = self._user_repo.get_user_profile(
            user_id=dto.user_id
        )
        dto.user_profile_id = user_profile.id if user_profile else None

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

                # 부양가족 수(본인 포함)
                # 3인 이하->0,1,2(3인 이하) / 3인->4 / 4인->5 / 5인->6 / 6인->7 / 7명 이상->8명 이상
                number_dependents_result: UserInfoEntity = UserRepository().get_user_info_by_code(
                    user_profile_id=user_info.user_profile_id,
                    code=CodeEnum.NUMBER_DEPENDENTS.value,
                )

                # 부양가족별 포함(본인 포함) basic 소득
                income_result: AvgMonthlyIncomeWokrerDto = UserRepository().get_avg_monthly_income_workers()
                income_result_dict = {
                    "0": income_result.three,  # 없어요 -> 1명(본인포함)
                    "1": income_result.three,  # 1명 -> 2명(본인포함)
                    "2": income_result.three,  # 2명 -> 3명(본인포함)
                    "3": income_result.four,  # 3명 -> 4명(본인포함)
                    "4": income_result.five,  # 4명 -> 5명(본인포함)
                    "5": income_result.six,  # 5명 -> 6명(본인포함)
                    "6": income_result.seven,  # 6명 -> 7명(본인포함)
                    "7": income_result.eight,  # 7명 이상 -> 8명 이상(본인포함)
                }

                calc_result_list = []

                if number_dependents_result:
                    # 가족 수 (부양가족 수 + 본인)
                    my_basic_income = income_result_dict.get(
                        str(number_dependents_result.value)
                    )

                    if not my_basic_income:
                        # todo. 가드 코드 추가(Sinbad 작업 후 제거 가능) #####################
                        my_basic_income = income_result_dict.get("1")
                        monthly_income_enum: List = MonthlyIncomeEnum.COND_CD_1.value
                        ##############################################################
                    else:
                        monthly_income_enum: List = MonthlyIncomeEnum.COND_CD_1.value if is_married_result.value != "2" else MonthlyIncomeEnum.COND_CD_2.value
                else:
                    # 설문 1단계를 완료 안하고 들어오지 못하지만 가드 코드 추가
                    # my_basic_income = 부양가족 3인 기본 값
                    # monthly_income_enum = 외벌이 기준
                    my_basic_income = income_result_dict.get("1")
                    monthly_income_enum: List = MonthlyIncomeEnum.COND_CD_1.value

                income_by_segment = None
                for idx_, percentage_num in enumerate(monthly_income_enum):
                    if idx_ == len(monthly_income_enum) - 1:
                        income_by_segment = str(income_by_segment) + "원 초과"
                        calc_result_list.append(income_by_segment)
                    else:
                        income_by_segment = (
                            int(my_basic_income) * percentage_num
                        ) / 100
                        income_by_segment = format(round(income_by_segment), ",d")
                        result_income_by_segment = str(income_by_segment) + "원 이하"
                        calc_result_list.append(result_income_by_segment)

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
        survey_step = (
            user.user_profile.survey_step
            if user.user_profile
            else UserSurveyStepEnum.STEP_NO.value
        )
        nickname = user.user_profile.nickname if user.user_profile else None

        return dict(
            survey_step=survey_step
            if survey_step
            else UserSurveyStepEnum.STEP_NO.value,
            tickets=user.total_amount,
            is_badge=is_badge,
            nickname=nickname,
        )

    def _get_badge(self, dto: GetUserDto) -> bool:
        dto = GetBadgeDto(user_id=dto.user_id)
        send_message(topic_name=NotificationTopicEnum.GET_BADGE, dto=dto)
        return get_event_object(topic_name=NotificationTopicEnum.GET_BADGE)


class GetSurveysUseCase(UserBaseUseCase):
    def execute(
        self, dto: GetUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        user_profile: Optional[UserProfileEntity] = self._user_repo.get_user_profile(
            user_id=dto.user_id
        )

        if not user_profile:
            return UseCaseFailureOutput(
                type="survey_result",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # 유저 설문 데이터 맵핑
        user_infos: List[GetSurveysBaseSchema] = self._make_user_info_object(
            user_profile=user_profile
        )

        return UseCaseSuccessOutput(value=user_infos)

    def _make_user_info_object(
        self, user_profile: UserProfileEntity
    ) -> List[GetSurveysBaseSchema]:
        result = list()
        code_dict = {
            # subjective = 주관식 변수 또는 바인딩 필요한 코드(거주지, 월소득)
            CodeEnum.NICKNAME.value: "subjective",
            CodeEnum.BIRTHDAY.value: "subjective",
            # 주택 소유 여부
            CodeEnum.IS_HOUSE_OWNER.value: dict(
                zip(
                    IsHouseOwnerCodeEnum.COND_CD.value,
                    IsHouseOwnerCodeEnum.COND_NM.value,
                )
            ),
            CodeEnum.SELL_HOUSE_DATE.value: "subjective",
            # 세대주 여부
            CodeEnum.IS_HOUSE_HOLDER.value: dict(
                zip(
                    IsHouseHolderCodeEnum.COND_CD.value,
                    IsHouseHolderCodeEnum.COND_NM.value,
                )
            ),
            # 주소
            CodeEnum.ADDRESS.value: "subjective",
            CodeEnum.ADDRESS_DETAIL.value: "subjective",
            CodeEnum.ADDRESS_DATE.value: "subjective",
            # 혼인
            CodeEnum.IS_MARRIED.value: dict(
                zip(IsMarriedCodeEnum.COND_CD.value, IsMarriedCodeEnum.COND_NM.value)
            ),
            CodeEnum.MARRIAGE_REG_DATE.value: "subjective",
            # 자녀
            CodeEnum.IS_CHILD.value: dict(
                zip(IsChildEnum.COND_CD.value, IsChildEnum.COND_NM.value)
            ),
            CodeEnum.CHILD_AGE_SIX.value: "subjective",
            CodeEnum.CHILD_AGE_NINETEEN.value: "subjective",
            CodeEnum.CHILD_AGE_TWENTY.value: "subjective",
            CodeEnum.MOST_CHILD_YOUNG_AGE.value: "subjective",
            # 청약통장
            CodeEnum.IS_SUB_ACCOUNT.value: dict(
                zip(IsSubAccountEnum.COND_CD.value, IsSubAccountEnum.COND_NM.value)
            ),
            CodeEnum.SUB_ACCOUNT_DATE.value: "subjective",
            CodeEnum.SUB_ACCOUNT_TIMES.value: "subjective",
            CodeEnum.SUB_ACCOUNT_TOTAL_PRICE.value: "subjective",
            # 소득
            CodeEnum.NUMBER_DEPENDENTS.value: dict(
                zip(
                    NumberDependentsEnum.COND_CD.value,
                    NumberDependentsEnum.COND_NM.value,
                )
            ),
            CodeEnum.MONTHLY_INCOME.value: "subjective",
            # 자산
            CodeEnum.ASSETS_REAL_ESTATE.value: dict(
                zip(
                    AssetsRealEstateEnum.COND_CD.value,
                    AssetsRealEstateEnum.COND_NM.value,
                )
            ),
            CodeEnum.ASSETS_CAR.value: dict(
                zip(AssetsCarEnum.COND_CD.value, AssetsCarEnum.COND_NM.value)
            ),
            CodeEnum.ASSETS_TOTAL.value: dict(
                zip(AssetsTotalEnum.COND_CD.value, AssetsTotalEnum.COND_NM.value)
            ),
            # 노부모 부양
            CodeEnum.SUPPORT_PARENT_DATE.value: "subjective",
            CodeEnum.IS_SUPPORT_PARENT.value: dict(
                zip(
                    IsSupportParentCodeEnum.COND_CD.value,
                    IsSupportParentCodeEnum.COND_NM.value,
                )
            ),
            # 기관 추천
            CodeEnum.SPECIAL_COND.value: dict(
                zip(SpecialCondEnum.COND_CD.value, SpecialCondEnum.COND_NM.value)
            ),
        }

        # 주소 맵핑 변수 초기화
        address_cnt, address_dict = 0, dict()
        # 총월소득 맵핑 변수 초기화
        monthly_income_flag, number_dependents, monthly_income_user_value = (
            False,
            0,
            None,
        )

        for user_info in user_profile.user_infos:
            if value := code_dict.get(user_info.code):
                value = (
                    value.get(int(user_info.user_value))
                    if value != "subjective"
                    else user_info.user_value
                )

                if (
                    user_info.code == CodeEnum.ADDRESS.value
                    or user_info.code == CodeEnum.ADDRESS_DETAIL.value
                ):
                    # 주소 맵핑
                    address_cnt += 1
                    address_dict[user_info.code] = user_info.user_value
                elif user_info.code == CodeEnum.MONTHLY_INCOME.value:
                    monthly_income_flag = True
                    monthly_income_user_value = value
                else:
                    base_schema = GetSurveysBaseSchema(code=user_info.code, value=value)
                    result.append(base_schema)

                    # 총월소득 계산위해 value 할당
                    if user_info.code == CodeEnum.NUMBER_DEPENDENTS.value:
                        number_dependents = int(user_info.user_value)

        if address_cnt == 2:
            sido_entity: SidoCodeEntity = self._user_repo.get_sido_name(
                sido_id=int(address_dict.get(CodeEnum.ADDRESS.value)),
                sigugun_id=int(address_dict.get(CodeEnum.ADDRESS_DETAIL.value)),
            )

            address_schema = GetSurveysBaseSchema(
                code=CodeEnum.ADDRESS.value, value=sido_entity.sido_name
            )
            address_detail_schema = GetSurveysBaseSchema(
                code=CodeEnum.ADDRESS_DETAIL.value, value=sido_entity.sigugun_name
            )
            result.extend([address_schema, address_detail_schema])

        if monthly_income_flag:
            # 월소득 맵핑
            # 부양가족별 포함(본인 포함) basic 소득
            income_result: AvgMonthlyIncomeWokrerDto = self._user_repo.get_avg_monthly_income_workers()
            income_result_dict = {
                0: income_result.three,
                1: income_result.three,
                2: income_result.three,
                3: income_result.four,
                4: income_result.five,
                5: income_result.six,
                6: income_result.seven,
                7: income_result.eight,
            }

            my_basic_income = income_result_dict.get(number_dependents)

            income_by_segment = my_basic_income * (int(monthly_income_user_value) / 100)
            income_by_segment = format(round(income_by_segment), ",d")
            result_income_by_segment = str(income_by_segment)

            if my_basic_income == income_result_dict.get(8):
                result_income_by_segment += "원 초과"
            else:
                result_income_by_segment += "원 이하"

            base_schema = GetSurveysBaseSchema(
                code=CodeEnum.MONTHLY_INCOME.value,
                value=[result_income_by_segment, monthly_income_user_value],
            )
            result.append(base_schema)
        return result


class GetUserProfileUseCase(UserBaseUseCase):
    def execute(
        self, dto: GetUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        user_profile: Optional[UserProfileEntity] = self._user_repo.get_user_profile(
            user_id=dto.user_id
        )
        return UseCaseSuccessOutput(value=user_profile)


class UpdateUserProfileUseCase(UserBaseUseCase):
    def execute(
        self, dto: UpdateUserProfileDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        if self._check_nickname_for_duplicate(nickname=dto.nickname):
            return UseCaseFailureOutput(
                type="duplicate nickname",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )

        # 기존 함수 사용 위해 dto 변환
        upsert_user_info_detail_dto = UpsertUserInfoDetailDto(
            user_id=dto.user_id, code=CodeEnum.NICKNAME.value, value=dto.nickname
        )
        user_profile: Optional[UserProfileEntity] = self._user_repo.get_user_profile(
            user_id=dto.user_id
        )

        if not user_profile:
            return UseCaseFailureOutput(
                type="user_profile_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        upsert_user_info_detail_dto.user_profile_id = user_profile.id

        # 닉네임 업데이트
        self._user_repo.update_user_nickname_of_profile_setting(
            dto=upsert_user_info_detail_dto
        )
        return UseCaseSuccessOutput()


class GetUserProviderUseCase(UserBaseUseCase):
    def execute(
        self, dto: GetUserProviderDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        response = requests.get(
            url=UserProviderCallEnum.CAPTAIN_BASE_URL.value
            + UserProviderCallEnum.CALL_END_POINT.value,
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Authorization": dto.auth_header,
            },
        )
        if response.status_code != HTTPStatus.OK:
            return UseCaseFailureOutput(
                type="provider",
                message=FailureType.INTERNAL_ERROR,
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        data = response.json()
        user: UserEntity = self._user_repo.get_user(user_id=dto.user_id)

        return UseCaseSuccessOutput(
            value=GetUserProviderBaseSchema(
                provider=data["data"]["provider"], email=user.email if user else None
            )
        )
