import uuid

import pytest

from app.persistence.model import InterestRegionModel, InterestRegionGroupModel, UserModel, AppAgreeTermModel
from core.domains.user.dto.user_dto import CreateUserDto, CreateAppAgreeTermDto
from core.domains.user.repository.user_repository import UserRepository
from core.domains.user.use_case.v1.user_use_case import CreateUserUseCase, CreateAppAgreeTerms
from core.exceptions import NotUniqueErrorException
from core.use_case_output import UseCaseSuccessOutput


def test_create_user_use_case_when_first_login_then_success(
        session, create_users, create_interest_region_groups
):
    dto = CreateUserDto(
        user_id=4,
        is_required_agree_terms=False,
        is_active=True,
        is_out=False,
        region_ids=[1],
        uuid=str(uuid.uuid4()),
        os="AOS",
        is_active_device=True,
        is_auth=False,
        token=str(uuid.uuid4()),
    )

    result = CreateUserUseCase().execute(dto=dto)

    interest_regions = (
        session.query(InterestRegionModel).filter_by(user_id=dto.user_id).all()
    )
    interest_region_groups = (
        session.query(InterestRegionGroupModel).filter_by(id=dto.region_ids[0]).first()
    )

    assert result.type == "success"
    assert isinstance(result, UseCaseSuccessOutput)
    assert len(interest_regions) == len(dto.region_ids)
    assert interest_region_groups.interest_count == 1


def test_create_user_when_first_login_with_duplicate_user_id_then_raise_unique_error(
        session, create_users, interest_region_group_factory
):
    user = create_users[0]
    interest_region_group_factory.create()

    dto = CreateUserDto(
        user_id=user.id,
        is_required_agree_terms=False,
        is_active=True,
        is_out=False,
        region_ids=[1],
        uuid=str(uuid.uuid4()),
        os="AOS",
        is_active_device=True,
        is_auth=False,
        token=str(uuid.uuid4()),
    )

    with pytest.raises(NotUniqueErrorException):
        CreateUserUseCase().execute(dto=dto)


def test_agree_terms_repo_when_app_first_start_with_not_receipt_marketing_then_success(
        session, create_users, interest_region_group_factory
):
    user = create_users[0]
    interest_region_group_factory.create()

    dto = CreateUserDto(
        user_id=user.id,
        is_required_agree_terms=False,
        is_active=True,
        is_out=False,
        region_ids=[1],
        uuid=str(uuid.uuid4()),
        os="AOS",
        is_active_device=True,
        is_auth=False,
        token=str(uuid.uuid4()),
    )

    with pytest.raises(NotUniqueErrorException):
        CreateUserUseCase().execute(dto=dto)


def test_agree_terms_repo_when_app_first_start_with_not_receipt_marketing_then_success(
        session
):
    create_user_dto = CreateUserDto(
        user_id=1,
        is_required_agree_terms=False,
        is_active=True,
        is_out=False,
        region_ids=[1],
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
        receipt_marketing_yn=True
    )

    UserRepository().create_user(dto=create_user_dto)
    CreateAppAgreeTerms().execute(dto=create_app_agree_term_dto)

    user = session.query(UserModel).filter_by(id=create_user_dto.user_id).first()
    app_agree_term = session.query(AppAgreeTermModel).filter_by(user_id=create_app_agree_term_dto.user_id).first()

    assert user.is_required_agree_terms is True
    assert app_agree_term.user_id == create_app_agree_term_dto.user_id
    assert app_agree_term.private_user_info_yn == create_app_agree_term_dto.private_user_info_yn
    assert app_agree_term.required_terms_yn == create_app_agree_term_dto.required_terms_yn
    assert app_agree_term.receipt_marketing_yn is True
    assert app_agree_term.receipt_marketing_date is not None

