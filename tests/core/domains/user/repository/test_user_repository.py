import uuid

import pytest

from app.persistence.model.user_model import UserModel
from core.domains.user.dto.user_dto import CreateUserDto
from core.domains.user.repository.user_repository import UserRepository
from core.exceptions import NotUniqueErrorException

create_user_dto = CreateUserDto(
    user_id=1,
    home_owner_type=1,
    interested_house_type=2,
    is_required_agree_terms=False,
    is_active=True,
    is_out=False,
    region_ids=[1],
    uuid=str(uuid.uuid4()),
    os="AOS",
    is_active_device=True,
    is_auth=False,
    token=str(uuid.uuid4())
)


def test_create_user_profiles_when_first_login_then_success(
        session, interest_region_factory
):
    UserRepository().create_user(dto=create_user_dto)
    interest_region_factory.create_batch(size=1, user_id=create_user_dto.user_id)

    user = session.query(UserModel).first()

    assert user.id == create_user_dto.user_id
    assert user.is_required_agree_terms == create_user_dto.is_required_agree_terms
    assert user.home_owner_type == create_user_dto.home_owner_type
    assert user.interested_house_type == create_user_dto.interested_house_type
    assert user.is_active == create_user_dto.is_active
    assert user.is_out == create_user_dto.is_out
    assert len(user.interest_regions) == len(create_user_dto.region_ids)


def test_create_user_profiles_with_dupulicate_id_when_first_login_then_not_unique_error(
        session,
):
    UserRepository().create_user(dto=create_user_dto)

    with pytest.raises(NotUniqueErrorException):
        UserRepository().create_user(dto=create_user_dto)
