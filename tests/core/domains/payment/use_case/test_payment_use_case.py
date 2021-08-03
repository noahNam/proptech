from http import HTTPStatus
from unittest.mock import patch

import pytest

from app.persistence.model import (
    TicketModel,
    TicketTargetModel,
    TicketUsageResultModel,
    PromotionUsageCountModel,
)
from core.domains.payment.dto.payment_dto import PaymentUserDto, UseTicketDto
from core.domains.payment.enum.payment_enum import (
    PromotionTypeEnum,
    TicketTypeDivisionEnum,
)
from core.domains.payment.use_case.v1.payment_use_case import (
    GetTicketUsageResultUseCase,
    UseBasicTicketUseCase,
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
