import io
from unittest.mock import patch

import pytest
from werkzeug.datastructures import FileStorage

from app.persistence.model import InterestRegionModel, InterestRegionGroupModel
from core.domains.user.dto.user_dto import CreateUserDto
from core.domains.user.use_case.v1.user_use_case import CreateUserUseCase
from core.exceptions import NotUniqueErrorException
from core.use_case_output import UseCaseSuccessOutput


@patch("app.extensions.utils.image_helper.S3Helper.upload", return_value=True)
def test_create_user_use_case_when_first_login_then_success(
    s3_upload_mock, session, create_users, interest_region_group_factory
):
    user = create_users[0]
    interest_region_group_factory.create_batch(3)

    # 실제 업로드 확인하려면 아래 경로에 이미지 첨부하고 patch, skip 데코레이터 제거한 뒤 실행.
    file_name = "/Users/noah/Downloads/profile_picture/noah.jpg"
    try:
        stream = io.open(file_name, "rb", buffering=0)
    except FileNotFoundError:
        stream = io.BytesIO(b"aaa")

    with stream as temp:
        file = FileStorage(
            stream=temp, filename=file_name, content_type="multipart/form-data",
        )

        dto = CreateUserDto(
            id=4,
            nickname=user.nickname,
            email=user.email,
            birthday=user.birthday,
            gender=user.gender,
            is_active=user.is_active,
            is_out=user.is_out,
            region_ids=[1, 2, 3],
            file=[file],
        )

        result = CreateUserUseCase().execute(dto=dto)

    interest_regions = (
        session.query(InterestRegionModel).filter_by(user_id=dto.id).all()
    )
    interest_region_groups = (
        session.query(InterestRegionGroupModel).filter_by(id=dto.region_ids[0]).first()
    )

    assert result.type == "success"
    assert isinstance(result, UseCaseSuccessOutput)
    assert len(interest_regions) == len(dto.region_ids)
    assert interest_region_groups.interest_count == 1


@patch("app.extensions.utils.image_helper.S3Helper.upload", return_value=False)
def test_create_user_when_img_upload_fail_then_success(
    s3_upload_mock, session, create_users, interest_region_group_factory
):
    user = create_users[0]
    interest_region_group_factory.create_batch(3)

    file_name = "/Users/noah/Downloads/profile_picture/noah.jpg"
    try:
        stream = io.open(file_name, "rb", buffering=0)
    except FileNotFoundError:
        stream = io.BytesIO(b"aaa")

    with stream as temp:
        file = FileStorage(
            stream=temp, filename=file_name, content_type="multipart/form-data",
        )

        dto = CreateUserDto(
            id=4,
            nickname=user.nickname,
            email=user.email,
            birthday=user.birthday,
            gender=user.gender,
            is_active=user.is_active,
            is_out=user.is_out,
            region_ids=[1, 2, 3],
            file=[file],
        )

        result = CreateUserUseCase().execute(dto=dto)

    interest_regions = (
        session.query(InterestRegionModel).filter_by(user_id=dto.id).all()
    )
    interest_region_groups = (
        session.query(InterestRegionGroupModel).filter_by(id=dto.region_ids[0]).first()
    )

    assert result.type == "success"
    assert isinstance(result, UseCaseSuccessOutput)
    assert len(interest_regions) == len(dto.region_ids)
    assert interest_region_groups.interest_count == 1


@patch("app.extensions.utils.image_helper.S3Helper.upload", return_value=True)
def test_create_user_when_first_login_with_duplicate_user_id_then_raise_unique_error(
    s3_upload_mock, session, create_users, interest_region_group_factory
):
    user = create_users[0]
    interest_region_group_factory.create()

    dto = CreateUserDto(
        id=user.id,
        nickname=user.nickname,
        email=user.email,
        birthday=user.birthday,
        gender=user.gender,
        is_active=user.is_active,
        is_out=user.is_out,
        region_ids=[1, 2, 3],
        file=[],
    )

    with pytest.raises(NotUniqueErrorException):
        CreateUserUseCase().execute(dto=dto)
