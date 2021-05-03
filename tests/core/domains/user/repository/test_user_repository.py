import uuid

import pytest
from pydantic import ValidationError

from app.persistence.model import UserProfileImgModel
from app.persistence.model.user_model import UserModel
from core.domains.user.dto.user_dto import CreateUserDto, CreateUserProfileImgDto
from core.domains.user.repository.user_repository import UserRepository
from core.exceptions import NotUniqueErrorException

create_user_dto = CreateUserDto(
    id=1,
    nickname="tester",
    email="test@gmail.com",
    birthday="19850509",
    gender="M",
    is_active=True,
    is_out=False,
    region_ids=[1, 2, 3]
)

create_user_profile_img_dto = CreateUserProfileImgDto(
    user_id=1,
    uuid_=str(uuid.uuid4()),
    file_name="my_profile_img",
    path="profile_imgs/",
    extension="png",
)


def test_create_user_profiles_when_first_login_then_success(session):
    UserRepository().create_user(dto=create_user_dto)
    user = session.query(UserModel).first()

    assert user.id == create_user_dto.id
    assert user.nickname == create_user_dto.nickname
    assert user.profile_img_id is None
    assert len(user.interest_regions) == len(create_user_dto.region_ids)


def test_create_user_profiles_without_required_value_when_first_login_then_validation_error(session):
    with pytest.raises(ValidationError):
        dummy_dto = CreateUserDto(
            nickname="tester",
            email="test@gmail.com",
            birthday="19850509",
            is_active=True,
            is_out=False,
            region_ids=[1, 2, 3]
        )
        UserRepository().create_user(dto=dummy_dto)


def test_create_user_profiles_with_dupulicate_id_when_first_login_then_not_unique_error(session):
    UserRepository().create_user(dto=create_user_dto)

    with pytest.raises(NotUniqueErrorException):
        UserRepository().create_user(dto=create_user_dto)


def test_create_user_profile_img_when_first_login_then_success(session):
    user_profile_img_id = UserRepository().create_user_profile_img(dto=create_user_profile_img_dto)
    user_profile_img = session.query(UserProfileImgModel).first()

    assert user_profile_img_id == 1
    assert user_profile_img.uuid == create_user_profile_img_dto.uuid_
    assert user_profile_img.file_name == create_user_profile_img_dto.file_name
    assert user_profile_img.path == create_user_profile_img_dto.path
    assert user_profile_img.extension == create_user_profile_img_dto.extension


def test_create_user_profile_img_without_user_id_when_first_login_then_validation_error(session):
    with pytest.raises(ValidationError):
        dummy_dto = CreateUserProfileImgDto(
            uuid_=str(uuid.uuid4()),
            file_name="my_profile_img",
            path="profile_imgs/",
            extension="png",
        )
        UserRepository().create_user_profile_img(dto=dummy_dto)
