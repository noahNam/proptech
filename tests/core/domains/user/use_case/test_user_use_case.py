import uuid

import pytest

from app.persistence.model import InterestRegionModel, InterestRegionGroupModel
from core.domains.user.dto.user_dto import CreateUserDto
from core.domains.user.use_case.v1.user_use_case import CreateUserUseCase
from core.exceptions import NotUniqueErrorException
from core.use_case_output import UseCaseSuccessOutput


def test_create_user_use_case_when_first_login_then_success(
        session, create_users, create_interest_region_groups
):
    dto = CreateUserDto(
        user_id=4,
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

    with pytest.raises(NotUniqueErrorException):
        CreateUserUseCase().execute(dto=dto)
