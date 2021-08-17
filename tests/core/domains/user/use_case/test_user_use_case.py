import uuid
from unittest.mock import patch

import pytest

from app.persistence.model import (
    UserModel,
    AppAgreeTermsModel,
    UserProfileModel,
    UserInfoModel,
    TicketModel,
)
from core.domains.payment.enum.payment_enum import TicketTypeDivisionEnum
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto,
    GetUserDto,
    UpsertUserInfoDetailDto,
    UpdateUserProfileDto,
)
from core.domains.user.entity.user_entity import UserInfoResultEntity, UserProfileEntity
from core.domains.user.enum.user_enum import UserSurveyStepEnum
from core.domains.user.enum.user_info_enum import (
    CodeEnum,
    MonthlyIncomeEnum,
    CodeStepEnum,
    IsHouseHolderCodeEnum,
)
from core.domains.user.repository.user_repository import UserRepository
from core.domains.user.use_case.v1.user_use_case import (
    CreateUserUseCase,
    CreateAppAgreeTermsUseCase,
    UpsertUserInfoUseCase,
    GetUserInfoUseCase,
    GetUserUseCase,
    UserOutUseCase,
    GetUserMainUseCase,
    GetSurveyResultUseCase,
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
)
from core.exceptions import NotUniqueErrorException
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput


def test_get_user_use_case_then_success(session, create_users):
    dto = GetUserDto(user_id=create_users[0].id,)

    result = GetUserUseCase().execute(dto=dto)

    assert result.type == "success"
    assert isinstance(result, UseCaseSuccessOutput)


def test_create_user_use_case_when_first_login_then_success(session, create_users):
    dto = CreateUserDto(
        user_id=4,
        is_required_agree_terms=False,
        is_active=True,
        is_out=False,
        uuid=str(uuid.uuid4()),
        os="AOS",
        is_active_device=True,
        is_auth=False,
        token=str(uuid.uuid4()),
    )

    result = CreateUserUseCase().execute(dto=dto)

    user = session.query(UserModel).filter_by(id=dto.user_id).first()

    assert result.type == "success"
    assert isinstance(result, UseCaseSuccessOutput)
    assert user.receive_push_type.is_official is True
    assert user.receive_push_type.is_private is True
    assert user.receive_push_type.is_marketing is True


def test_create_user_when_first_login_with_duplicate_user_id_then_raise_unique_error(
    session, create_users
):
    user = create_users[0]

    dto = CreateUserDto(
        user_id=user.id,
        is_required_agree_terms=False,
        is_active=True,
        is_out=False,
        uuid=str(uuid.uuid4()),
        os="AOS",
        is_active_device=True,
        is_auth=False,
        token=str(uuid.uuid4()),
    )

    with pytest.raises(NotUniqueErrorException):
        CreateUserUseCase().execute(dto=dto)


def test_agree_terms_repo_when_app_first_start_with_not_receive_marketing_then_success(
    session, create_users, interest_region_group_factory
):
    user = create_users[0]
    interest_region_group_factory.create()

    dto = CreateUserDto(
        user_id=user.id,
        is_required_agree_terms=False,
        is_active=True,
        is_out=False,
        uuid=str(uuid.uuid4()),
        os="AOS",
        is_active_device=True,
        is_auth=False,
        token=str(uuid.uuid4()),
    )

    with pytest.raises(NotUniqueErrorException):
        CreateUserUseCase().execute(dto=dto)


def test_agree_terms_repo_when_app_first_start_with_not_receive_marketing_then_success(
    session,
):
    create_user_dto = CreateUserDto(
        user_id=1,
        is_required_agree_terms=False,
        is_active=True,
        is_out=False,
        uuid=str(uuid.uuid4()),
        os="AOS",
        is_active_device=True,
        is_auth=False,
        token=str(uuid.uuid4()),
    )

    create_app_agree_term_dto = CreateAppAgreeTermsDto(
        user_id=1,
        private_user_info_yn=True,
        required_terms_yn=True,
        receive_marketing_yn=True,
    )

    UserRepository().create_user(dto=create_user_dto)
    CreateAppAgreeTermsUseCase().execute(dto=create_app_agree_term_dto)

    user = session.query(UserModel).filter_by(id=create_user_dto.user_id).first()
    app_agree_term = (
        session.query(AppAgreeTermsModel)
        .filter_by(user_id=create_app_agree_term_dto.user_id)
        .first()
    )

    assert user.is_required_agree_terms is True
    assert app_agree_term.user_id == create_app_agree_term_dto.user_id
    assert (
        app_agree_term.private_user_info_yn
        == create_app_agree_term_dto.private_user_info_yn
    )
    assert (
        app_agree_term.required_terms_yn == create_app_agree_term_dto.required_terms_yn
    )
    assert app_agree_term.receive_marketing_yn is True
    assert app_agree_term.receive_marketing_date is not None


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_upsert_user_info_when_create_nickname_then_success(
    _send_sqs_message, session, create_users
):
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1000], values=["noah"]
    )

    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)
    user_profile = (
        session.query(UserProfileModel)
        .filter_by(user_id=upsert_user_info_dto.user_id)
        .first()
    )

    assert user_profile.id == 1
    assert user_profile.user_id == upsert_user_info_dto.user_id
    assert user_profile.nickname == upsert_user_info_dto.values[0]
    assert user_profile.last_update_code == upsert_user_info_dto.codes[0]


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_upsert_user_info_when_update_nickname_then_success(
    _send_sqs_message, session, create_users
):
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1000], values=["noah"]
    )

    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    upsert_user_info_dto.values[0] = "noah2"
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    user_profile = (
        session.query(UserProfileModel)
        .filter_by(user_id=upsert_user_info_dto.user_id)
        .first()
    )

    assert user_profile.id == 1
    assert user_profile.user_id == upsert_user_info_dto.user_id
    assert user_profile.nickname == upsert_user_info_dto.values[0]
    assert user_profile.last_update_code == upsert_user_info_dto.codes[0]


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_upsert_user_info_when_create_user_data_then_success(
    _send_sqs_message, session, create_users
):
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1005], values=["1"]
    )

    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    user_profile = (
        session.query(UserProfileModel)
        .filter_by(user_id=upsert_user_info_dto.user_id)
        .first()
    )
    user_info = (
        session.query(UserInfoModel)
        .filter_by(user_profile_id=user_profile.id, code=upsert_user_info_dto.codes[0])
        .first()
    )
    ticket = (
        session.query(TicketModel)
        .filter_by(
            user_id=upsert_user_info_dto.user_id,
            type=TicketTypeDivisionEnum.SURVEY_PROMOTION.value,
        )
        .first()
    )

    assert user_profile.last_update_code == upsert_user_info_dto.codes[0]
    assert user_info.user_profile_id == user_profile.id
    assert user_info.code == upsert_user_info_dto.codes[0]
    assert user_info.value == upsert_user_info_dto.values[0]
    assert ticket is None


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_upsert_user_info_when_update_user_data_then_success(
    _send_sqs_message, session, create_users
):
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1005], values=["1"]
    )

    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    upsert_user_info_dto.values[0] = "2"
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    user_profile = (
        session.query(UserProfileModel)
        .filter_by(user_id=upsert_user_info_dto.user_id)
        .first()
    )
    user_info = (
        session.query(UserInfoModel)
        .filter_by(user_profile_id=user_profile.id, code=upsert_user_info_dto.codes[0])
        .first()
    )

    assert user_profile.last_update_code == upsert_user_info_dto.codes[0]
    assert user_info.user_profile_id == user_profile.id
    assert user_info.code == upsert_user_info_dto.codes[0]
    assert user_info.value == upsert_user_info_dto.values[0]


def test_get_user_info_when_first_input_surveys_then_get_none_user_data(
    session, create_users
):
    get_user_info_dto = GetUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, survey_step=1,
    )
    result = GetUserInfoUseCase().execute(dto=get_user_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, list)
    assert len(result.value) == len(CodeStepEnum.ONE.value)

    for value in result.value:
        if value.code == 1000:
            assert value.code_values is None
            assert value.user_value is None


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_get_user_info_when_secondary_input_nickname_then_get_user_data(
    _send_sqs_message, session
):
    user_id = 1
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=user_id, user_profile_id=None, codes=[1000], values=["noah"]
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    get_user_info_dto = GetUserInfoDto(
        user_id=user_id, user_profile_id=None, survey_step=1,
    )
    result = GetUserInfoUseCase().execute(dto=get_user_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, list)
    assert len(result.value) == len(CodeStepEnum.ONE.value)

    for value in result.value:
        if value.code == upsert_user_info_dto.codes[0]:
            assert value.code_values is None
            assert value.user_value == upsert_user_info_dto.values[0]


def test_get_user_info_when_first_input_data_then_get_none_user_data(
    session, create_users
):
    get_user_info_dto = GetUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, survey_step=1,
    )
    result = GetUserInfoUseCase().execute(dto=get_user_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, list)
    assert len(result.value) == len(CodeStepEnum.ONE.value)

    for value in result.value:
        if value.code == CodeEnum.IS_HOUSE_HOLDER.value:
            assert len(value.code_values.detail_code) == len(
                IsHouseHolderCodeEnum.COND_CD.value
            )
            assert value.user_value is None


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_get_user_info_when_secondary_input_data_then_get_user_data(
    _send_sqs_message, session, create_users
):
    user_id = 1
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=user_id, user_profile_id=None, codes=[1005], values=["2"]
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    get_user_info_dto = GetUserInfoDto(
        user_id=user_id, user_profile_id=None, survey_step=1,
    )
    result = GetUserInfoUseCase().execute(dto=get_user_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, list)
    assert isinstance(result.value[0], UserInfoResultEntity)
    assert len(result.value) == len(CodeStepEnum.ONE.value)


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_get_user_info_when_monthly_income_then_success(
    _send_sqs_message, session, create_users, avg_monthly_income_worker_factory
):
    avg_monthly_income_workers = avg_monthly_income_worker_factory.build()
    session.add(avg_monthly_income_workers)
    session.commit()

    # 외벌이, 맞벌이 확인
    # 외벌이 -> 1,3,4 / 맞벌이 -> 2
    upsert_user_info_dto = UpsertUserInfoDetailDto(
        user_id=create_users[0].id,
        user_profile_id=create_users[0].id,
        code=CodeEnum.IS_MARRIED.value,
        value="2",
    )
    UserRepository().create_user_info(dto=upsert_user_info_dto)

    # 부양가족 수
    # 3인 이하->1,2,3 / 4인->4 / 5인->5 / 6인->6 / 7인->7 / 8명 이상->8 / 없어요->9
    upsert_user_info_dto = UpsertUserInfoDetailDto(
        user_id=create_users[0].id,
        user_profile_id=create_users[0].id,
        code=CodeEnum.NUMBER_DEPENDENTS.value,
        value="5",
    )
    UserRepository().create_user_info(dto=upsert_user_info_dto)

    # Data 조회
    get_user_info_dto = GetUserInfoDto(
        user_id=create_users[0].id, user_profile_id=create_users[0].id, survey_step=2,
    )
    result = GetUserInfoUseCase().execute(dto=get_user_info_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    for value in result.value:
        if value.code == CodeEnum.MONTHLY_INCOME.value:
            assert len(value.code_values.detail_code) == len(
                MonthlyIncomeEnum.COND_CD_2.value
            )
            assert value.user_value is None

            # 맞벌이, 부양가족 5인
            assert value.code_values.name == [
                "3,547,102원 이하",
                "5,675,364원 이하",
                "7,803,626원 이하",
                "8,513,046원 이하",
                "9,222,466원 이하",
                "9,931,887원 이하",
                "11,350,728원 이하",
                "11,350,728원 초과",
            ]


def test_patch_user_out_info_when_user_request_then_success(session, create_users):
    get_user_dto = GetUserDto(user_id=create_users[0].id)
    result = UserOutUseCase().execute(dto=get_user_dto)

    assert isinstance(result, UseCaseSuccessOutput)


def test_get_user_main_use_case_when_enter_my_page_main_then_ticket_is_0_and_survey_step_is_step_one_and_badge_is_true(
    session, create_users, create_notifications
):
    get_user_dto = GetUserDto(user_id=create_users[0].id)
    result = GetUserMainUseCase().execute(dto=get_user_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value["survey_step"] == UserSurveyStepEnum.STEP_ONE.value
    assert result.value["tickets"] == 0
    assert result.value["is_badge"] is True


def test_get_survey_result_use_case_then_return_user_nickname_and_birth_and_survey_results(
    session, create_users
):
    get_user_dto = GetUserDto(user_id=create_users[0].id)
    result = GetSurveyResultUseCase().execute(dto=get_user_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, dict)
    assert result.value["age"] == 36
    assert result.value["user_profile_entity"].nickname == "noah"
    assert result.value["user_profile_entity"].user_infos[0].user_value == "19850509"
    assert result.value["user_profile_entity"].survey_result.total_point == 32


def test_get_survey_result_use_case_then_return_survey_result_is_none(
    session, create_users
):
    get_user_dto = GetUserDto(user_id=create_users[1].id)
    result = GetSurveyResultUseCase().execute(dto=get_user_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, dict)
    assert result.value["age"] == 36
    assert result.value["user_profile_entity"].nickname == "noah"
    assert result.value["user_profile_entity"].user_infos[0].user_value == "19850509"
    assert result.value["user_profile_entity"].survey_result is None


def test_get_user_profile_use_case_when_enter_setting_page_return_success(
    session, create_users
):
    user_1 = GetUserDto(user_id=create_users[1].id)
    user_2 = GetUserDto(user_id=4)

    result_1 = GetUserProfileUseCase().execute(dto=user_1)
    result_2 = GetUserProfileUseCase().execute(dto=user_2)

    assert isinstance(result_1, UseCaseSuccessOutput)
    assert isinstance(result_2, UseCaseSuccessOutput)
    assert isinstance(result_1.value, UserProfileEntity)
    assert result_2.value is None


def test_update_user_profile_use_case_when_enter_setting_page_return_success(
    session, create_users
):
    dto = UpdateUserProfileDto(user_id=create_users[0].id, nickname="harry")
    result_1 = UpdateUserProfileUseCase().execute(dto=dto)

    dto = GetUserDto(user_id=create_users[0].id)
    result_2 = GetUserProfileUseCase().execute(dto=dto)

    assert isinstance(result_1, UseCaseSuccessOutput)
    assert result_1.type == "success"
    assert result_2.value.nickname == "harry"


def test_update_user_profile_use_case_when_enter_duplicate_nickname_return_failure(
    session, create_users
):
    dto = UpdateUserProfileDto(user_id=create_users[0].id, nickname="noah")
    result = UpdateUserProfileUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.type == "duplicate nickname"
    assert result.message == "invalid_request_error"


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_upsert_user_info_when_update_is_house_owner_then_chain_update_user_data(
    _send_sqs_message, session, create_users
):
    """
        1. 1005: 주택 소유 여부 질문 (3) -> "있어요", "없어요", "과거에 있었지만 현재는 처분했어요"
           1006: 주택 처분 날짜 -> 202107
        2. 1005: 주택 소유 여부 질문 (1) -> "있어요", "없어요", "과거에 있었지만 현재는 처분했어요"
        Then. 1006 value == None
    """
    # 1
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id,
        user_profile_id=None,
        codes=[1005, 1006],
        values=["3", "202107"],
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    # 2
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1005], values=["1"]
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    # Then
    user_profile = (
        session.query(UserProfileModel)
        .filter_by(user_id=upsert_user_info_dto.user_id)
        .first()
    )
    user_infos = (
        session.query(UserInfoModel)
        .filter(
            UserInfoModel.user_profile_id == user_profile.id,
            UserInfoModel.code.in_([1005, 1006]),
        )
        .all()
    )

    assert user_profile.survey_step == UserSurveyStepEnum.STEP_ONE.value
    for user_info in user_infos:
        if user_info.code == 1006:
            assert user_info.value is None


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_upsert_user_info_when_update_is_sub_account_then_chain_update_user_data(
    _send_sqs_message, session, create_users
):
    """
        1. 1016: 청약 통장 여부 질문 (1) -> "있어요", "없어요"
           1017: 청약 가입 날짜 -> 202107
           1019: 납입횟수 -> 24
           1020: 총금액 -> 30000
        2. 1016: 주택 소유 여부 질문 (2) -> "있어요", "없어요"
        Then. 1017,1019,1020 value == None
    """
    # 1
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id,
        user_profile_id=None,
        codes=[1016, 1017, 1018, 1019],
        values=["1", "202107", "24", "30000"],
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    # 2
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1016], values=["2"]
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    # Then
    user_profile = (
        session.query(UserProfileModel)
        .filter_by(user_id=upsert_user_info_dto.user_id)
        .first()
    )
    user_infos = (
        session.query(UserInfoModel)
        .filter(
            UserInfoModel.user_profile_id == user_profile.id,
            UserInfoModel.code.in_([1016, 1017, 1018, 1019]),
        )
        .all()
    )

    ticket = (
        session.query(TicketModel)
        .filter_by(
            user_id=upsert_user_info_dto.user_id,
            type=TicketTypeDivisionEnum.SURVEY_PROMOTION.value,
        )
        .first()
    )

    assert user_profile.survey_step == UserSurveyStepEnum.STEP_TWO.value
    assert ticket is None
    for user_info in user_infos:
        if user_info.code == 1016:
            assert user_info.value == "2"
        else:
            assert user_info.value is None


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_upsert_user_info_when_update_is_sub_account_then_survey_step_is_two(
    _send_sqs_message, session, create_users
):
    """
        1. 1016: 청약 통장 여부 질문 (2) -> "있어요", "없어요"
        Then. survey_step == 2
    """
    # 1
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1016], values=["2"],
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    # Then
    user_profile = (
        session.query(UserProfileModel)
        .filter_by(user_id=upsert_user_info_dto.user_id)
        .first()
    )

    assert user_profile.survey_step == UserSurveyStepEnum.STEP_TWO.value


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_upsert_user_info_when_update_is_sub_account_then_survey_step_is_one(
    _send_sqs_message, session, create_users
):
    """
        1. 1016: 청약 통장 여부 질문 (1) -> "있어요", "없어요"
        Then. survey_step == 1
    """
    # 1
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1016], values=["1"],
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    # Then
    user_profile = (
        session.query(UserProfileModel)
        .filter_by(user_id=upsert_user_info_dto.user_id)
        .first()
    )

    assert user_profile.survey_step == UserSurveyStepEnum.STEP_ONE.value


@patch(
    "core.domains.user.use_case.v1.user_use_case.UpsertUserInfoUseCase._send_sqs_message",
    return_value=True,
)
def test_upsert_user_info_when_update_speical_cond_then_survey_step_is_comepte(
    _send_sqs_message, session, create_users
):
    """
        1. code == 1026
        Then. survey_step == 3
    """
    # 설문 2단계 set
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1016], values=["2"],
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    # 1
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1026], values=["2"],
    )
    UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    # Then
    user_profile = (
        session.query(UserProfileModel)
        .filter_by(user_id=upsert_user_info_dto.user_id)
        .first()
    )

    ticket = (
        session.query(TicketModel)
        .filter_by(
            user_id=upsert_user_info_dto.user_id,
            type=TicketTypeDivisionEnum.SURVEY_PROMOTION.value,
        )
        .first()
    )

    assert user_profile.survey_step == UserSurveyStepEnum.STEP_COMPLETE.value
    assert ticket.type == TicketTypeDivisionEnum.SURVEY_PROMOTION.value


def test_upsert_user_info_when_update_duplicate_nickname_then_failure(
    session, create_users
):
    upsert_user_info_dto = UpsertUserInfoDto(
        user_id=create_users[0].id, user_profile_id=None, codes=[1000], values=["noah"],
    )
    result = UpsertUserInfoUseCase().execute(dto=upsert_user_info_dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.type == "duplicate nickname"
    assert result.message == "invalid_request_error"
