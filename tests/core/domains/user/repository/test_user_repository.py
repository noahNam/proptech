import uuid

import pytest

from app.persistence.model import AppAgreeTermsModel, UserProfileModel, UserInfoModel
from app.persistence.model.user_model import UserModel
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto,
)
from core.domains.user.entity.user_entity import (
    UserInfoEntity,
    UserInfoEmptyEntity, UserEntity,
)
from core.domains.user.repository.user_repository import UserRepository
from core.exceptions import NotUniqueErrorException

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
    receipt_marketing_yn=False,
)

upsert_user_info_dto = UpsertUserInfoDto(
    user_id=1, user_profile_id=1, code=1005, value="1"
)


def test_get_user_repo_then_success(create_users):
    user = UserRepository().get_user(create_users[0].id)
    assert isinstance(user, UserEntity)
    assert user.is_required_agree_terms == create_users[0].is_required_agree_terms
    assert user.id == create_users[0].id
    assert user.is_out == create_users[0].is_out
    assert user.is_active == create_users[0].is_active


def test_create_user_profiles_when_first_login_then_success(
        session, interest_region_factory
):
    UserRepository().create_user(dto=create_user_dto)
    interest_region_factory.create_batch(size=1, user_id=create_user_dto.user_id)

    user = session.query(UserModel).first()

    assert user.id == create_user_dto.user_id
    assert user.is_required_agree_terms == create_user_dto.is_required_agree_terms
    assert user.is_active == create_user_dto.is_active
    assert user.is_out == create_user_dto.is_out


def test_create_user_profiles_with_dupulicate_id_when_first_login_then_not_unique_error(
        session,
):
    UserRepository().create_user(dto=create_user_dto)

    with pytest.raises(NotUniqueErrorException):
        UserRepository().create_user(dto=create_user_dto)


def test_agree_terms_repo_when_app_first_start_with_not_receipt_marketing_then_success(
        session,
):
    UserRepository().create_app_agree_terms(dto=create_app_agree_term_dto)

    result = session.query(AppAgreeTermsModel).filter_by(user_id=1).first()
    assert result.user_id == create_app_agree_term_dto.user_id
    assert result.private_user_info_yn == create_app_agree_term_dto.private_user_info_yn
    assert result.required_terms_yn == create_app_agree_term_dto.required_terms_yn
    assert result.receipt_marketing_yn == create_app_agree_term_dto.receipt_marketing_yn
    assert result.receipt_marketing_date is None


def test_agree_terms_repo_when_app_first_start_with_receipt_marketing_then_success(
        session,
):
    create_app_agree_term_dto.receipt_marketing_yn = True
    UserRepository().create_app_agree_terms(dto=create_app_agree_term_dto)

    result = session.query(AppAgreeTermsModel).filter_by(user_id=1).first()
    assert result.user_id == create_app_agree_term_dto.user_id
    assert result.private_user_info_yn == create_app_agree_term_dto.private_user_info_yn
    assert result.required_terms_yn == create_app_agree_term_dto.required_terms_yn
    assert result.receipt_marketing_yn is True
    assert result.receipt_marketing_date is not None


def test_update_user_required_agree_terms_when_app_first_start_then_success(session):
    # user.is_required_agree_terms = False
    UserRepository().create_user(dto=create_user_dto)
    UserRepository().update_user_required_agree_terms(dto=create_app_agree_term_dto)

    result = session.query(UserModel).filter_by(id=create_user_dto.user_id).first()
    assert result.is_required_agree_terms is True


def test_create_user_nickname_when_start_user_info_then_success(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_dto)
    result = (
        session.query(UserProfileModel)
            .filter_by(user_id=upsert_user_info_dto.user_id)
            .first()
    )

    assert result.nickname == upsert_user_info_dto.value
    assert result.last_update_code == upsert_user_info_dto.code


def test_update_user_nickname_when_update_user_info_then_success(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_dto)

    upsert_user_info_dto.value = "noah2"
    UserRepository().update_user_nickname(dto=upsert_user_info_dto)

    result = (
        session.query(UserProfileModel)
            .filter_by(user_id=upsert_user_info_dto.user_id)
            .first()
    )

    assert result.nickname == "noah2"
    assert result.last_update_code == upsert_user_info_dto.code


def test_create_user_info_when_input_user_data_then_success(session):
    UserRepository().create_user_info(dto=upsert_user_info_dto)

    result = (
        session.query(UserInfoModel)
            .filter_by(
            user_profile_id=upsert_user_info_dto.user_profile_id,
            code=upsert_user_info_dto.code,
        )
            .first()
    )

    assert result.user_profile_id == upsert_user_info_dto.user_profile_id
    assert result.code == upsert_user_info_dto.code
    assert result.value == upsert_user_info_dto.value


def test_create_user_info_when_input_user_data_without_profile_id_then_error(
        session, create_users
):
    dto = UpsertUserInfoDto(user_id=create_users[0].id, code=1005, value="1")
    with pytest.raises(NotUniqueErrorException):
        UserRepository().create_user_info(dto=dto)


def test_update_user_info_when_input_user_data_then_success(session):
    UserRepository().create_user_info(dto=upsert_user_info_dto)

    upsert_user_info_dto.value = "2"
    UserRepository().update_user_info(dto=upsert_user_info_dto)

    result = (
        session.query(UserInfoModel)
            .filter_by(
            user_profile_id=upsert_user_info_dto.user_profile_id,
            code=upsert_user_info_dto.code,
        )
            .first()
    )

    assert result.user_profile_id == upsert_user_info_dto.user_profile_id
    assert result.code == upsert_user_info_dto.code
    assert result.value == "2"


def test_update_last_code_to_user_info_when_input_user_data_then_success(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_dto)

    dto = UpsertUserInfoDto(
        user_id=upsert_user_info_dto.user_id, user_profile_id=1, code=1007, value="2"
    )
    UserRepository().update_last_code_to_user_info(dto=dto)

    result = session.query(UserProfileModel).filter_by(user_id=dto.user_id).first()

    assert result.last_update_code == dto.code


def test_get_user_profile_id_when_input_user_data_then_success(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_dto)
    get_user_profile_id = UserRepository().get_user_profile_id(dto=upsert_user_info_dto)

    assert get_user_profile_id == 1


def test_get_user_profile_id_when_input_user_data_then_none(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_dto)

    upsert_user_info_dto.user_id = upsert_user_info_dto.user_id + 1
    get_user_profile_id = UserRepository().get_user_profile_id(dto=upsert_user_info_dto)

    assert get_user_profile_id is None


def test_get_user_info_when_input_user_data_then_success(session):
    UserRepository().create_user_info(dto=upsert_user_info_dto)
    dto = GetUserInfoDto(
        user_id=upsert_user_info_dto.user_id,
        user_profile_id=upsert_user_info_dto.user_profile_id,
        code=upsert_user_info_dto.code,
    )

    user_info: UserInfoEntity = UserRepository().get_user_info(dto=dto)

    assert user_info.user_profile_id == dto.user_profile_id
    assert user_info.code == dto.code
    assert user_info.user_value == upsert_user_info_dto.value


def test_get_user_info_when_input_user_data_then_None(session):
    UserRepository().create_user_info(dto=upsert_user_info_dto)
    dto = GetUserInfoDto(
        user_id=upsert_user_info_dto.user_id,
        user_profile_id=upsert_user_info_dto.user_profile_id,
        code=upsert_user_info_dto.code + 1,
        value=upsert_user_info_dto.value,
    )

    user_info: UserInfoEmptyEntity = UserRepository().get_user_info(dto=dto)

    assert isinstance(user_info, UserInfoEmptyEntity)
