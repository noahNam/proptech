import uuid

import pytest

from app.persistence.model import AppAgreeTermModel
from app.persistence.model.user_model import UserModel
from core.domains.user.dto.user_dto import CreateUserDto, CreateAppAgreeTermDto
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

create_app_agree_term_dto = CreateAppAgreeTermDto(
    user_id=1,
    private_user_info_yn=True,
    required_terms_yn=True,
    receipt_marketing_yn=False
)


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
        session
):
    UserRepository().create_app_agree_terms(dto=create_app_agree_term_dto)

    result = session.query(AppAgreeTermModel).filter_by(user_id=1).first()
    assert result.user_id == create_app_agree_term_dto.user_id
    assert result.private_user_info_yn == create_app_agree_term_dto.private_user_info_yn
    assert result.required_terms_yn == create_app_agree_term_dto.required_terms_yn
    assert result.receipt_marketing_yn == create_app_agree_term_dto.receipt_marketing_yn
    assert result.receipt_marketing_date is None


def test_agree_terms_repo_when_app_first_start_with_receipt_marketing_then_success(
        session
):
    create_app_agree_term_dto.receipt_marketing_yn = True
    UserRepository().create_app_agree_terms(dto=create_app_agree_term_dto)

    result = session.query(AppAgreeTermModel).filter_by(user_id=1).first()
    assert result.user_id == create_app_agree_term_dto.user_id
    assert result.private_user_info_yn == create_app_agree_term_dto.private_user_info_yn
    assert result.required_terms_yn == create_app_agree_term_dto.required_terms_yn
    assert result.receipt_marketing_yn is True
    assert result.receipt_marketing_date is not None


def test_update_user_required_agree_terms_when_app_first_start_then_success(
        session
):
    # user.is_required_agree_terms = False
    UserRepository().create_user(dto=create_user_dto)
    UserRepository().update_user_required_agree_terms(dto=create_app_agree_term_dto)

    result = session.query(UserModel).filter_by(id=create_user_dto.user_id).first()
    assert result.is_required_agree_terms is True
