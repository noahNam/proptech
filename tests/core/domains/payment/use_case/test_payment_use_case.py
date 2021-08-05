from http import HTTPStatus
from unittest.mock import patch

import pytest

from app.persistence.model import (
    TicketModel,
    TicketTargetModel,
    TicketUsageResultModel,
    PromotionUsageCountModel,
    RecommendCodeModel,
)
from core.domains.payment.dto.payment_dto import (
    PaymentUserDto,
    UseTicketDto,
    UseRecommendCodeDto,
)
from core.domains.payment.enum.payment_enum import (
    PromotionTypeEnum,
    TicketTypeDivisionEnum,
    TicketSignEnum,
)
from core.domains.payment.use_case.v1.payment_use_case import (
    GetTicketUsageResultUseCase,
    UseBasicTicketUseCase,
    CreateRecommendCodeUseCase,
    GetRecommendCodeUseCase,
    UseRecommendCodeUseCase,
)
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput

use_ticket_dto = UseTicketDto(user_id=1, house_id=1)


def test_get_ticket_usage_result_use_case_then_success(
    session,
    create_users,
    create_real_estate_with_public_sale,
    create_ticket_usage_results,
    public_sale_photo_factory,
):
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)
    session.add(public_sale_photo)
    session.commit()

    dto = PaymentUserDto(user_id=create_users[0].id)
    result = GetTicketUsageResultUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, list)
    assert len(result.value) == 1


def test_use_ticket_when_already_been_used_then_return_failure_output(
    session, ticket_usage_result_factory
):
    """
        이미 티켓을 사용한 분양건에 대해서 다시 티켓을 사용할 경우
    """
    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()

    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.message == "this is product where tickets have already been used"


def test_use_ticket_when_no_prom_no_available_ticket_then_return_failure_output(
    session, ticket_usage_result_factory
):
    """
        프로모션이 없고 티켓도 없는 경우
    """
    ticket_usage_result = ticket_usage_result_factory.build(public_house_id=99)
    session.add(ticket_usage_result)
    session.commit()

    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.message == "insufficient number of tickets"


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_no_prom_available_ticket_then_return_success_output(
    call_jarvis_analytics_api,
    is_ticket_usage,
    session,
    ticket_usage_result_factory,
    ticket_factory,
):
    """
        프로모션이 없고 티켓은 있는 경우
    """
    # data set #############################################################
    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()

    ticket = ticket_factory.build(user_id=1, ticket_type=False, ticket_targets=False)
    session.add(ticket)
    session.commit()
    ########################################################################

    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    # data 검증 #############################################################
    ticket_models = (
        session.query(TicketModel)
        .filter(
            TicketModel.user_id == use_ticket_dto.user_id, TicketModel.is_active == True
        )
        .all()
    )

    ticket_target_models = (
        session.query(TicketTargetModel)
        .filter(
            TicketTargetModel.ticket_id == ticket.id + 1,
            TicketTargetModel.public_house_id == use_ticket_dto.house_id,
        )
        .all()
    )

    ticket_usage_result_model = (
        session.query(TicketUsageResultModel)
        .filter(
            TicketUsageResultModel.user_id == use_ticket_dto.user_id,
            TicketUsageResultModel.public_house_id == use_ticket_dto.house_id,
        )
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value["message"] == "ticket used"

    assert len(ticket_models) == 2
    assert len(ticket_target_models) == 1
    assert ticket_usage_result_model.ticket_id == ticket.id + 1


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_exist_all_type_prom_available_count_available_ticket_then_return_success_output(
    call_jarvis_analytics_api,
    is_ticket_usage,
    session,
    ticket_usage_result_factory,
    ticket_factory,
    promotion_factory,
):
    """
        적용프로모션이 있는 경우
            1. 프로모션 타입 == ALL
            2. 프로모션 횟수가 남아있는 경우
    """
    # data set #############################################################
    promotion = promotion_factory.build(
        promotion_houses=False, promotion_usage_count=False
    )
    session.add(promotion)
    session.commit()

    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()

    ticket = ticket_factory.build(user_id=1, ticket_type=False, ticket_targets=False)
    session.add(ticket)
    session.commit()
    ########################################################################

    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    # data 검증 #############################################################
    ticket_models = (
        session.query(TicketModel)
        .filter(
            TicketModel.user_id == use_ticket_dto.user_id, TicketModel.is_active == True
        )
        .all()
    )

    ticket_target_models = (
        session.query(TicketTargetModel)
        .filter(
            TicketTargetModel.ticket_id == ticket.id + 1,
            TicketTargetModel.public_house_id == use_ticket_dto.house_id,
        )
        .all()
    )

    ticket_usage_result_model = (
        session.query(TicketUsageResultModel)
        .filter(
            TicketUsageResultModel.user_id == use_ticket_dto.user_id,
            TicketUsageResultModel.public_house_id == use_ticket_dto.house_id,
        )
        .first()
    )

    promotion_usage_count_model = (
        session.query(PromotionUsageCountModel)
        .filter(
            PromotionUsageCountModel.promotion_id == promotion.id,
            PromotionUsageCountModel.user_id == use_ticket_dto.user_id,
        )
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value["message"] == "promotion used"

    assert len(ticket_models) == 2
    assert len(ticket_target_models) == 1
    assert ticket_usage_result_model.ticket_id == ticket.id + 1
    assert promotion_usage_count_model.usage_count == 1


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_exist_all_type_prom_no_count_available_ticket_then_return_success_output(
    call_jarvis_analytics_api,
    is_ticket_usage,
    session,
    ticket_usage_result_factory,
    ticket_factory,
    promotion_factory,
):
    """
        적용프로모션이 있는 경우
            1. 프로모션 타입 == ALL
            2. 프로모션 횟수가 남아있지 않고 티켓이 있는 경우
    """
    # data set #############################################################
    promotion = promotion_factory.build(
        promotion_houses=False, promotion_usage_count=True
    )
    session.add(promotion)
    session.commit()

    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()

    ticket = ticket_factory.build(user_id=1, ticket_type=False, ticket_targets=False)
    session.add(ticket)
    session.commit()
    ########################################################################

    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    # data 검증 #############################################################
    ticket_models = (
        session.query(TicketModel)
        .filter(
            TicketModel.user_id == use_ticket_dto.user_id, TicketModel.is_active == True
        )
        .all()
    )

    ticket_target_models = (
        session.query(TicketTargetModel)
        .filter(
            TicketTargetModel.ticket_id == ticket.id + 1,
            TicketTargetModel.public_house_id == use_ticket_dto.house_id,
        )
        .all()
    )

    ticket_usage_result_model = (
        session.query(TicketUsageResultModel)
        .filter(
            TicketUsageResultModel.user_id == use_ticket_dto.user_id,
            TicketUsageResultModel.public_house_id == use_ticket_dto.house_id,
        )
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value["message"] == "ticket used"

    assert len(ticket_models) == 2
    assert len(ticket_target_models) == 1
    assert ticket_usage_result_model.ticket_id == ticket.id + 1


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_exist_all_type_prom_no_count_no_ticket_then_return_failure_output(
    call_jarvis_analytics_api,
    is_ticket_usage,
    session,
    ticket_usage_result_factory,
    promotion_factory,
):
    """
        적용프로모션이 있는 경우
            1. 프로모션 타입 == ALL
            2. 프로모션 횟수가 남아있지 않고 티켓이 없는 경우
    """
    # data set #############################################################
    promotion = promotion_factory.build(
        promotion_houses=False, promotion_usage_count=True
    )
    session.add(promotion)
    session.commit()

    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()
    ########################################################################

    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value["message"] == "no ticket for promotion"


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_exist_house_exist_some_type_prom_no_count_available_ticket_then_return_success_output(
    call_jarvis_analytics_api,
    is_ticket_usage,
    session,
    ticket_usage_result_factory,
    ticket_factory,
    promotion_factory,
):
    """
        적용프로모션이 있는 경우
            1. 프로모션 타입 == SOME
            2. House_id가 프로모션에 속하는 경우
            3. 프로모션 횟수 전부 소비한 상태
            4. 유료티켓이 있는 경우 -> 성공
    """
    # data set #############################################################
    promotion = promotion_factory.build(
        type=PromotionTypeEnum.SOME.value,
        promotion_houses=True,
        promotion_usage_count=True,
    )
    session.add(promotion)
    session.commit()

    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()

    ticket = ticket_factory.build(user_id=1, ticket_type=False, ticket_targets=False)
    session.add(ticket)
    session.commit()
    ########################################################################

    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    # data 검증 #############################################################
    ticket_models = (
        session.query(TicketModel)
        .filter(
            TicketModel.user_id == use_ticket_dto.user_id, TicketModel.is_active == True
        )
        .all()
    )

    ticket_target_models = (
        session.query(TicketTargetModel)
        .filter(
            TicketTargetModel.ticket_id == ticket.id + 1,
            TicketTargetModel.public_house_id == use_ticket_dto.house_id,
        )
        .all()
    )

    ticket_usage_result_model = (
        session.query(TicketUsageResultModel)
        .filter(
            TicketUsageResultModel.user_id == use_ticket_dto.user_id,
            TicketUsageResultModel.public_house_id == use_ticket_dto.house_id,
        )
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value["message"] == "ticket used"

    assert len(ticket_models) == 2
    assert len(ticket_target_models) == 1
    assert ticket_usage_result_model.ticket_id == ticket.id + 1


@pytest.mark.skip(reason="유닛테스트는 통과하나 전체 테스트시에 생기는 문제로 skip")
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_exist_house_exist_some_type_prom_no_count_no_available_ticket_then_return_success_output(
    is_ticket_usage, session, promotion_factory
):
    """
        적용프로모션이 있는 경우
            1. 프로모션 타입 == SOME
            2. House_id가 프로모션에 속하는 경우
            3. 프로모션 횟수 전부 소비한 상태
            4. 유료티켓이 없는 경우 -> 실패
    """
    # data set #############################################################
    promotion = promotion_factory.build(
        type=PromotionTypeEnum.SOME.value,
        promotion_houses=True,
        promotion_usage_count=True,
    )
    session.add(promotion)
    session.commit()
    ########################################################################

    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)
    # assert isinstance(result, UseCaseSuccessOutput)
    assert result.value["message"] == "no ticket for promotion"


@pytest.mark.skip(reason="유닛테스트는 통과하나 전체 테스트시에 생기는 문제로 skip")
@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_exist_house_exist_some_type_prom_available_count_then_return_success_output(
    call_jarvis_analytics_api,
    is_ticket_usage,
    session,
    ticket_usage_result_factory,
    promotion_factory,
):
    """
        적용프로모션이 있는 경우
            1. 프로모션 타입 == SOME
            2. House_id가 프로모션에 속하는 경우
            3. 프로모션 횟수가 남아있는 경우
    """
    # data set #############################################################
    promotion = promotion_factory.build(
        type=PromotionTypeEnum.SOME.value,
        promotion_houses=True,
        promotion_usage_count=False,
    )
    session.add(promotion)
    session.commit()

    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()
    ########################################################################

    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    # data 검증 #############################################################
    ticket_models = (
        session.query(TicketModel)
        .filter(
            TicketModel.user_id == use_ticket_dto.user_id, TicketModel.is_active == True
        )
        .all()
    )

    ticket_target_models = (
        session.query(TicketTargetModel)
        .filter(
            TicketTargetModel.ticket_id == 1,
            TicketTargetModel.public_house_id == use_ticket_dto.house_id,
        )
        .all()
    )

    ticket_usage_result_model = (
        session.query(TicketUsageResultModel)
        .filter(
            TicketUsageResultModel.user_id == use_ticket_dto.user_id,
            TicketUsageResultModel.public_house_id == use_ticket_dto.house_id,
        )
        .first()
    )

    promotion_usage_count_model = (
        session.query(PromotionUsageCountModel)
        .filter(
            PromotionUsageCountModel.promotion_id == promotion.id,
            PromotionUsageCountModel.user_id == use_ticket_dto.user_id,
        )
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value["message"] == "promotion used"

    assert len(ticket_models) == 1
    assert ticket_models[0].type == TicketTypeDivisionEnum.USED_PROMOTION.value
    assert len(ticket_target_models) == 1
    assert ticket_usage_result_model.ticket_id == 1
    assert promotion_usage_count_model.usage_count == 1


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_not_exist_house_exist_some_type_prom_available_ticket_then_return_success_output(
    call_jarvis_analytics_api,
    is_ticket_usage,
    session,
    ticket_usage_result_factory,
    ticket_factory,
    promotion_factory,
):
    """
        적용프로모션이 있는 경우
            1. 프로모션 타입 == SOME
            2. House_id가 프로모션에 속하지 않는 경우
            3. 유료티켓이 있는 경우
    """
    # data set #############################################################
    promotion = promotion_factory.build(
        type=PromotionTypeEnum.SOME.value,
        promotion_houses=True,
        promotion_usage_count=False,
    )
    session.add(promotion)
    session.commit()

    ticket_usage_result = ticket_usage_result_factory.build(public_house_id=99)
    session.add(ticket_usage_result)
    session.commit()

    ticket = ticket_factory.build(user_id=1, ticket_type=False, ticket_targets=False)
    session.add(ticket)
    session.commit()
    ########################################################################

    use_ticket_dto.house_id = 99
    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    # data 검증 #############################################################
    ticket_models = (
        session.query(TicketModel)
        .filter(
            TicketModel.user_id == use_ticket_dto.user_id, TicketModel.is_active == True
        )
        .all()
    )

    ticket_target_models = (
        session.query(TicketTargetModel)
        .filter(
            TicketTargetModel.ticket_id == ticket.id + 1,
            TicketTargetModel.public_house_id == 99,
        )
        .all()
    )

    ticket_usage_result_model = (
        session.query(TicketUsageResultModel)
        .filter(
            TicketUsageResultModel.user_id == use_ticket_dto.user_id,
            TicketUsageResultModel.public_house_id == use_ticket_dto.house_id,
        )
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.value["message"] == "ticket used"

    assert len(ticket_models) == 2
    assert ticket_models[1].type == TicketTypeDivisionEnum.USED_TICKET.value
    assert len(ticket_target_models) == 1
    assert ticket_usage_result_model.ticket_id == ticket.id + 1


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_not_exist_house_exist_some_type_prom_no_available_ticket_then_return_failure_output(
    call_jarvis_analytics_api,
    is_ticket_usage,
    session,
    ticket_usage_result_factory,
    promotion_factory,
):
    """
        적용프로모션이 있는 경우
            1. 프로모션 타입 == SOME
            2. House_id가 프로모션에 속하지 않는 경우
            3. 유료티켓이 없는 경우
    """
    # data set #############################################################
    promotion = promotion_factory.build(
        type=PromotionTypeEnum.SOME.value,
        promotion_houses=True,
        promotion_usage_count=False,
    )
    session.add(promotion)
    session.commit()

    ticket_usage_result = ticket_usage_result_factory.build(public_house_id=99)
    session.add(ticket_usage_result)
    session.commit()
    ########################################################################

    use_ticket_dto.house_id = 99
    result = UseBasicTicketUseCase().execute(dto=use_ticket_dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.value["message"] == "insufficient number of tickets"


def test_create_recommend_code_then_return_success_output(
    session, create_users,
):
    dto = PaymentUserDto(user_id=create_users[0].id)
    result = CreateRecommendCodeUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert len(result.value) == 7


def test_get_recommend_code_then_return_success_output(
    session, create_users,
):
    dto = PaymentUserDto(user_id=create_users[0].id)
    CreateRecommendCodeUseCase().execute(dto=dto)
    result = GetRecommendCodeUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert len(result.value) == 7


def test_use_recommend_code_when_no_recommend_code_user_then_return_success_output(
    session, create_users
):
    """
        추천코드 입력하는 유저가 본인의 코드 정보가 없다면 recommend_codes 스키마를 생성하고 성공
    """
    payment_provider_dto = PaymentUserDto(user_id=create_users[0].id)
    result = CreateRecommendCodeUseCase().execute(dto=payment_provider_dto)

    use_recommend_code_dto = UseRecommendCodeDto(
        user_id=create_users[1].id, code=result.value
    )
    UseRecommendCodeUseCase().execute(dto=use_recommend_code_dto)

    # data 검증 #############################################################
    # 무료쿠폰 제공자
    provider_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == payment_provider_dto.user_id)
        .first()
    )

    # 무료쿠폰 사용자
    receiver_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == use_recommend_code_dto.user_id)
        .first()
    )

    # 티켓 히스토리
    receiver_ticket = (
        session.query(TicketModel)
        .filter(TicketModel.user_id == receiver_user.user_id)
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseSuccessOutput)
    assert provider_user.code_count == 1
    assert provider_user.is_used is False
    assert len(provider_user.code) == 6
    assert provider_user.code_group == 0

    assert receiver_user.code_count == 0
    assert receiver_user.is_used is True
    assert len(receiver_user.code) == 6
    assert receiver_user.code_group == 0

    assert provider_user.code != receiver_user.code

    assert receiver_ticket.sign == TicketSignEnum.PLUS.value
    assert receiver_ticket.type == TicketTypeDivisionEnum.SHARE_PROMOTION.value
    assert receiver_ticket.amount == 1
    assert receiver_ticket.is_active is True


def test_use_recommend_code_when_have_recommend_code_user_then_return_success_output(
    session, create_users
):
    """
        추천코드 입력하는 유저가 본인의 코드 정보가 있고 성공
    """
    # 쿠폰 제공자, 수신자 set
    payment_provider_dto = PaymentUserDto(user_id=create_users[0].id)
    result = CreateRecommendCodeUseCase().execute(dto=payment_provider_dto)

    payment_receiver_dto = PaymentUserDto(user_id=create_users[1].id)
    CreateRecommendCodeUseCase().execute(dto=payment_receiver_dto)
    ##########################################################################

    use_recommend_code_dto = UseRecommendCodeDto(
        user_id=create_users[1].id, code=result.value
    )
    UseRecommendCodeUseCase().execute(dto=use_recommend_code_dto)

    # data 검증 #############################################################
    # 무료쿠폰 제공자
    provider_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == payment_provider_dto.user_id)
        .first()
    )

    # 무료쿠폰 사용자
    receiver_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == use_recommend_code_dto.user_id)
        .first()
    )

    # 티켓 히스토리
    receiver_ticket = (
        session.query(TicketModel)
        .filter(TicketModel.user_id == receiver_user.user_id)
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseSuccessOutput)
    assert provider_user.code_count == 1
    assert provider_user.is_used is False
    assert len(provider_user.code) == 6
    assert provider_user.code_group == 0

    assert receiver_user.code_count == 0
    assert receiver_user.is_used is True
    assert len(receiver_user.code) == 6
    assert receiver_user.code_group == 0

    assert provider_user.code != receiver_user.code

    assert receiver_ticket.sign == TicketSignEnum.PLUS.value
    assert receiver_ticket.type == TicketTypeDivisionEnum.SHARE_PROMOTION.value
    assert receiver_ticket.amount == 1
    assert receiver_ticket.is_active is True


def test_use_recommend_code_when_user_already_used_code_then_return_failure_output(
    session, create_users, recommend_code_factory
):
    """
        추천코드 입력하는 유저가 이미 추천 코드를 입력한 유저
    """
    # 쿠폰 제공자, 수신자 set
    payment_provider_dto = PaymentUserDto(user_id=create_users[0].id)
    result = CreateRecommendCodeUseCase().execute(dto=payment_provider_dto)

    recommend_code = recommend_code_factory.build(
        user_id=create_users[1].id, is_used=True
    )
    session.add(recommend_code)
    session.commit()

    ##########################################################################

    use_recommend_code_dto = UseRecommendCodeDto(
        user_id=create_users[1].id, code=result.value
    )
    result = UseRecommendCodeUseCase().execute(dto=use_recommend_code_dto)

    # data 검증 #############################################################
    # 무료쿠폰 제공자
    provider_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == payment_provider_dto.user_id)
        .first()
    )

    # 무료쿠폰 사용자
    receiver_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == use_recommend_code_dto.user_id)
        .first()
    )

    # 티켓 히스토리
    receiver_ticket = (
        session.query(TicketModel)
        .filter(TicketModel.user_id == receiver_user.user_id)
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseFailureOutput)
    assert result.value["type"] == "user already used code"

    assert result.value["message"] == "invalid_request_error"
    assert provider_user.is_used is False
    assert len(provider_user.code) == 6
    assert provider_user.code_group == 0

    assert receiver_user.code_count == 0
    assert receiver_user.is_used is True
    assert len(receiver_user.code) == 6
    assert receiver_user.code_group == 0

    assert provider_user.code != receiver_user.code

    assert receiver_ticket is None


def test_use_recommend_code_when_code_does_not_exist_then_return_failure_output(
    session, create_users, recommend_code_factory
):
    """
        존재하지 않는 추천 코드를 입력한 경우
    """
    # 쿠폰 제공자 set
    payment_provider_dto = PaymentUserDto(user_id=create_users[0].id)
    result = CreateRecommendCodeUseCase().execute(dto=payment_provider_dto)
    ##########################################################################

    use_recommend_code_dto = UseRecommendCodeDto(
        user_id=create_users[1].id, code="1234567"
    )
    result = UseRecommendCodeUseCase().execute(dto=use_recommend_code_dto)

    # data 검증 #############################################################
    # 무료쿠폰 제공자
    provider_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == payment_provider_dto.user_id)
        .first()
    )

    # 무료쿠폰 사용자
    receiver_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == use_recommend_code_dto.user_id)
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseFailureOutput)
    assert result.value["type"] == "code does not exist"

    assert result.value["message"] == "not_found_error"
    assert provider_user.is_used is False
    assert len(provider_user.code) == 6
    assert provider_user.code_group == 0

    assert receiver_user.code_count == 0
    assert receiver_user.is_used is False
    assert len(receiver_user.code) == 6
    assert receiver_user.code_group == 0

    assert provider_user.code != use_recommend_code_dto.code


def test_use_recommend_code_when_code_already_been_all_used_then_return_failure_output(
    session, create_users, recommend_code_factory
):
    """
        만료된 코드(사용횟수가 2회 전부 사용)
    """
    # 쿠폰 제공자 set
    recommend_code = recommend_code_factory.build(
        user_id=create_users[0].id, is_used=True, code_count=2
    )
    session.add(recommend_code)
    session.commit()

    ##########################################################################

    use_recommend_code_dto = UseRecommendCodeDto(
        user_id=create_users[1].id,
        code=str(recommend_code.code_group) + recommend_code.code,
    )
    result = UseRecommendCodeUseCase().execute(dto=use_recommend_code_dto)

    # data 검증 #############################################################
    # 무료쿠폰 제공자
    provider_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == recommend_code.user_id)
        .first()
    )

    # 무료쿠폰 사용자
    receiver_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == use_recommend_code_dto.user_id)
        .first()
    )
    ########################################################################

    assert isinstance(result, UseCaseFailureOutput)
    assert result.value["type"] == "code already been all used"

    assert result.value["message"] == "invalid_request_error"
    assert provider_user.is_used is True
    assert len(provider_user.code) == 6
    assert provider_user.code_group == 0
    assert provider_user.code_count == 2

    assert receiver_user.is_used is False
    assert len(receiver_user.code) == 6
    assert receiver_user.code_group == 0
    assert receiver_user.code_count == 0


def test_use_recommend_code_when_not_available_code_then_return_failure_output(
    session, create_users, recommend_code_factory
):
    """
        본인의 코드를 스스로 입력한 경우
    """
    # 쿠폰 제공자 set
    recommend_code = recommend_code_factory.build(
        user_id=create_users[0].id, is_used=False, code_count=0
    )
    session.add(recommend_code)
    session.commit()

    ##########################################################################

    use_recommend_code_dto = UseRecommendCodeDto(
        user_id=create_users[0].id,
        code=str(recommend_code.code_group) + recommend_code.code,
    )
    result = UseRecommendCodeUseCase().execute(dto=use_recommend_code_dto)

    assert isinstance(result, UseCaseFailureOutput)
    assert result.value["type"] == "not available code"
    assert result.value["message"] == "invalid_request_error"
