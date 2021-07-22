import uuid
from typing import List

import pytest

from app.persistence.model import AppAgreeTermsModel, UserProfileModel, UserInfoModel, RecentlyViewModel
from app.persistence.model.user_model import UserModel
from core.domains.user.dto.user_dto import (
    CreateUserDto,
    CreateAppAgreeTermsDto,
    UpsertUserInfoDto,
    GetUserInfoDto, AvgMonthlyIncomeWokrerDto, UpsertUserInfoDetailDto, GetUserInfoDetailDto, RecentlyViewDto,
)
from core.domains.user.entity.user_entity import (
    UserInfoEntity,
    UserInfoEmptyEntity, UserEntity, UserInfoCodeValueEntity,
)
from core.domains.user.enum.user_info_enum import IsHouseOwnerCodeEnum, IsHouseHolderCodeEnum, IsMarriedCodeEnum, \
    NumberDependentsEnum, IsChildEnum, IsSubAccountEnum, MonthlyIncomeEnum, AssetsRealEstateEnum, AssetsCarEnum, \
    AssetsTotalEnum, SpecialCondEnum, CodeEnum
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
    receive_marketing_yn=False,
)

upsert_user_info_detail_dto = UpsertUserInfoDto(
    user_id=1, user_profile_id=1, codes=[1005], values=["1"]
)

upsert_user_info_detail_dto = UpsertUserInfoDetailDto(
    user_id=1, user_profile_id=1, code=1005, value="1"
)

recently_view_dto = RecentlyViewDto(
    user_id=1, house_id=1, type=1
)


def test_get_user_repo_then_success(create_users):
    user = UserRepository().get_user(create_users[0].id)
    assert isinstance(user, UserEntity)
    assert user.is_required_agree_terms == create_users[0].is_required_agree_terms
    assert user.id == create_users[0].id
    assert user.is_out == create_users[0].is_out
    assert user.is_active == create_users[0].is_active


def test_create_user_profiles_when_first_login_then_success(
        session
):
    UserRepository().create_user(dto=create_user_dto)

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


def test_agree_terms_repo_when_app_first_start_with_not_receive_marketing_then_success(
        session,
):
    UserRepository().create_app_agree_terms(dto=create_app_agree_term_dto)

    result = session.query(AppAgreeTermsModel).filter_by(user_id=1).first()
    assert result.user_id == create_app_agree_term_dto.user_id
    assert result.private_user_info_yn == create_app_agree_term_dto.private_user_info_yn
    assert result.required_terms_yn == create_app_agree_term_dto.required_terms_yn
    assert result.receive_marketing_yn == create_app_agree_term_dto.receive_marketing_yn
    assert result.receive_marketing_date is None


def test_agree_terms_repo_when_app_first_start_with_receive_marketing_then_success(
        session,
):
    create_app_agree_term_dto.receive_marketing_yn = True
    UserRepository().create_app_agree_terms(dto=create_app_agree_term_dto)

    result = session.query(AppAgreeTermsModel).filter_by(user_id=1).first()
    assert result.user_id == create_app_agree_term_dto.user_id
    assert result.private_user_info_yn == create_app_agree_term_dto.private_user_info_yn
    assert result.required_terms_yn == create_app_agree_term_dto.required_terms_yn
    assert result.receive_marketing_yn is True
    assert result.receive_marketing_date is not None


def test_update_user_required_agree_terms_when_app_first_start_then_success(session):
    # user.is_required_agree_terms = False
    UserRepository().create_user(dto=create_user_dto)
    UserRepository().update_user_required_agree_terms(dto=create_app_agree_term_dto)

    result = session.query(UserModel).filter_by(id=create_user_dto.user_id).first()
    assert result.is_required_agree_terms is True


def test_create_user_nickname_when_start_user_info_then_success(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_detail_dto)
    result = (
        session.query(UserProfileModel)
            .filter_by(user_id=upsert_user_info_detail_dto.user_id)
            .first()
    )

    assert result.nickname == upsert_user_info_detail_dto.value
    assert result.last_update_code == upsert_user_info_detail_dto.code


def test_update_user_nickname_when_update_user_info_then_success(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_detail_dto)

    upsert_user_info_detail_dto.value = "noah2"
    UserRepository().update_user_nickname(dto=upsert_user_info_detail_dto)

    result = (
        session.query(UserProfileModel)
            .filter_by(user_id=upsert_user_info_detail_dto.user_id)
            .first()
    )

    assert result.nickname == "noah2"
    assert result.last_update_code == upsert_user_info_detail_dto.code


def test_create_user_info_when_input_user_data_then_success(session):
    UserRepository().create_user_info(dto=upsert_user_info_detail_dto)

    result = (
        session.query(UserInfoModel)
            .filter_by(
            user_profile_id=upsert_user_info_detail_dto.user_profile_id,
            code=upsert_user_info_detail_dto.code,
        )
            .first()
    )

    assert result.user_profile_id == upsert_user_info_detail_dto.user_profile_id
    assert result.code == upsert_user_info_detail_dto.code
    assert result.value == upsert_user_info_detail_dto.value


def test_create_user_info_when_input_user_data_without_profile_id_then_error(
        session, create_users
):
    dto = UpsertUserInfoDetailDto(user_id=create_users[0].id, code=1005, value="1")
    with pytest.raises(NotUniqueErrorException):
        UserRepository().create_user_info(dto=dto)


def test_update_user_info_when_input_user_data_then_success(session):
    UserRepository().create_user_info(dto=upsert_user_info_detail_dto)

    upsert_user_info_detail_dto.value = "2"
    UserRepository().update_user_info(dto=upsert_user_info_detail_dto)

    result = (
        session.query(UserInfoModel)
            .filter_by(
            user_profile_id=upsert_user_info_detail_dto.user_profile_id,
            code=upsert_user_info_detail_dto.code,
        )
            .first()
    )

    assert result.user_profile_id == upsert_user_info_detail_dto.user_profile_id
    assert result.code == upsert_user_info_detail_dto.code
    assert result.value == "2"


def test_update_last_code_to_user_info_when_input_user_data_then_success(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_detail_dto)

    dto = UpsertUserInfoDetailDto(
        user_id=upsert_user_info_detail_dto.user_id, user_profile_id=1, code=1007, value="2"
    )
    UserRepository().update_last_code_to_user_info(dto=dto)

    result = session.query(UserProfileModel).filter_by(user_id=dto.user_id).first()

    assert result.last_update_code == dto.code


def test_get_user_profile_id_when_input_user_data_then_success(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_detail_dto)
    get_user_profile_id = UserRepository().get_user_profile_id(dto=upsert_user_info_detail_dto)

    assert get_user_profile_id == 1


def test_get_user_profile_id_when_input_user_data_then_none(session):
    UserRepository().create_user_nickname(dto=upsert_user_info_detail_dto)

    upsert_user_info_detail_dto.user_id = upsert_user_info_detail_dto.user_id + 1
    get_user_profile_id = UserRepository().get_user_profile_id(dto=upsert_user_info_detail_dto)

    assert get_user_profile_id is None


def test_get_user_info_when_input_user_data_then_success(session):
    UserRepository().create_user_info(dto=upsert_user_info_detail_dto)
    dto = GetUserInfoDetailDto(
        user_id=upsert_user_info_detail_dto.user_id,
        user_profile_id=upsert_user_info_detail_dto.user_profile_id,
        code=upsert_user_info_detail_dto.code,
    )

    user_info: UserInfoEntity = UserRepository().get_user_info(dto=dto)

    assert user_info.code == dto.code
    assert user_info.user_value[0] == upsert_user_info_detail_dto.value


def test_get_user_info_when_input_user_data_then_None(session):
    UserRepository().create_user_info(dto=upsert_user_info_detail_dto)
    dto = GetUserInfoDetailDto(
        user_id=upsert_user_info_detail_dto.user_id,
        code=upsert_user_info_detail_dto.code + 1,
        value=upsert_user_info_detail_dto.value,
    )

    user_info: UserInfoEmptyEntity = UserRepository().get_user_info(dto=dto)

    assert isinstance(user_info, UserInfoEmptyEntity)


def test_get_avg_monthly_income_workers_when_input_user_data_then_success(avg_monthly_income_worker_factory, session,
                                                                          create_users):
    avg_monthly_income_workers = avg_monthly_income_worker_factory.build()
    session.add(avg_monthly_income_workers)
    session.commit()

    income_result: AvgMonthlyIncomeWokrerDto = UserRepository().get_avg_monthly_income_workers()

    assert isinstance(income_result, AvgMonthlyIncomeWokrerDto)
    assert income_result.three == avg_monthly_income_workers.three
    assert income_result.four == avg_monthly_income_workers.four
    assert income_result.five == avg_monthly_income_workers.five
    assert income_result.six == avg_monthly_income_workers.six
    assert income_result.seven == avg_monthly_income_workers.seven
    assert income_result.eight == avg_monthly_income_workers.eight

    # 외벌이, 맞벌이 확인
    # 외벌이 -> 1,3,4 / 맞벌이 -> 2
    upsert_user_info_detail_dto = UpsertUserInfoDetailDto(
        user_id=1, user_profile_id=1, code=CodeEnum.IS_MARRIED.value, value="2"
    )
    UserRepository().create_user_info(dto=upsert_user_info_detail_dto)

    # 부양가족 수
    # 3인 이하->1,2,3 / 4인->4 / 5인->5 / 6인->6 / 7인->7 / 8명 이상->8 / 없어요->9
    upsert_user_info_detail_dto = UpsertUserInfoDetailDto(
        user_id=1, user_profile_id=1, code=CodeEnum.NUMBER_DEPENDENTS.value, value="5"
    )
    UserRepository().create_user_info(dto=upsert_user_info_detail_dto)

    user_info_code = str(CodeEnum.MONTHLY_INCOME.value)

    bind_detail_code_dict = {
        "1005": IsHouseOwnerCodeEnum,
        "1007": IsHouseHolderCodeEnum,
        "1008": IsMarriedCodeEnum,
        "1010": NumberDependentsEnum,
        "1011": IsChildEnum,
        "1015": IsSubAccountEnum,
        "1019": MonthlyIncomeEnum,
        "1020": AssetsRealEstateEnum,
        "1021": AssetsCarEnum,
        "1022": AssetsTotalEnum,
        "1025": SpecialCondEnum,
    }

    user_info = UserInfoEntity(id=1, user_profile_id=1, code=user_info_code)
    bind_code = bind_detail_code_dict.get(user_info_code)
    # dto.code != "1019" 일 떄로 변경
    dto_code = "1019"
    if dto_code != "1019":

        user_info_code_value_entity = UserInfoCodeValueEntity()
        user_info_code_value_entity.detail_code = bind_code.COND_CD.value
        user_info_code_value_entity.name = bind_code.COND_NM.value

        user_info.code_values = user_info_code_value_entity
    else:
        # 외벌이, 맞벌이 확인
        # 외벌이 -> 1,3,4 / 맞벌이 -> 2
        result1: UserInfoEntity = UserRepository().get_user_info_by_code(
            user_profile_id=upsert_user_info_detail_dto.user_profile_id, code=CodeEnum.IS_MARRIED.value)

        # 부양가족 수
        # 3인 이하->1,2,3,9 / 4인->4 / 5인->5 / 6인->6 / 7인->7 / 8명 이상->8
        result2: UserInfoEntity = UserRepository().get_user_info_by_code(
            user_profile_id=upsert_user_info_detail_dto.user_profile_id, code=CodeEnum.NUMBER_DEPENDENTS.value)

        # 부양가족별 default 소득
        income_result_dict = {
            "1": income_result.three,
            "2": income_result.three,
            "3": income_result.three,
            "4": income_result.four,
            "5": income_result.five,
            "6": income_result.six,
            "7": income_result.seven,
            "8": income_result.eight,
            "9": income_result.three,
        }

        calc_result_list = []
        my_basic_income = income_result_dict.get(result2.user_value)

        monthly_income_enum: List = MonthlyIncomeEnum.COND_CD_1.value if result1.user_value != "2" else MonthlyIncomeEnum.COND_CD_2.value

        for percentage_num in monthly_income_enum:
            income_by_segment = (int(my_basic_income) * percentage_num) / 100
            income_by_segment = round(income_by_segment)
            calc_result_list.append(income_by_segment)

        user_info_code_value_entity = UserInfoCodeValueEntity()

        user_info_code_value_entity.detail_code = monthly_income_enum
        user_info_code_value_entity.name = calc_result_list

        user_info.code_values = user_info_code_value_entity

        assert isinstance(user_info, UserInfoEntity)
        assert len(user_info.code_values.detail_code) == len(user_info.code_values.name)


def test_update_user_status_to_out_when_user_want_memeber_out_then_return_1(session, create_users):
    UserRepository().update_user_status_to_out(user_id=create_users[0].id)
    user = UserRepository().get_user(user_id=create_users[0].id)

    assert user.is_out is True


def test_create_recently_view_table(session):
    UserRepository().create_recently_view(dto=recently_view_dto)
    view_info = session.query(RecentlyViewModel).first()

    assert view_info.user_id == recently_view_dto.user_id
    assert view_info.house_id == recently_view_dto.house_id
    assert view_info.type == recently_view_dto.type
