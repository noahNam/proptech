from app.persistence.model import (
    TicketUsageResultModel,
    PromotionUsageCountModel,
    TicketTargetModel,
)
from core.domains.payment.dto.payment_dto import (
    PaymentUserDto,
    UseTicketDto,
    CreateUseTicketDto,
    UpdateTicketUsageResultDto,
)
from core.domains.payment.entity.payment_entity import PromotionEntity
from core.domains.payment.enum.payment_enum import TicketSignEnum
from core.domains.payment.repository.payment_repository import PaymentRepository


def test_get_ticket_usage_results_then_return_public_sale_ids(
    session,
    create_users,
    create_real_estate_with_public_sale,
    create_ticket_usage_results,
    public_sale_photo_factory,
):
    public_sales_id = 1
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=public_sales_id)
    session.add(public_sale_photo)
    session.commit()

    dto = PaymentUserDto(user_id=create_users[0].id)
    result = PaymentRepository().get_ticket_usage_results(dto=dto)

    assert len(result) == 1
    assert result[0] == public_sales_id


def test_is_ticket_usage_then_return_true(
    session, create_users, ticket_usage_result_factory
):
    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()

    dto = UseTicketDto(user_id=create_users[0].id, house_id=1)
    result = PaymentRepository().is_ticket_usage(dto=dto)

    assert isinstance(result, bool)
    assert result is True


def test_is_ticket_usage_then_return_false(
    session, create_users, ticket_usage_result_factory
):
    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()

    dto = UseTicketDto(user_id=create_users[0].id, house_id=2)
    result = PaymentRepository().is_ticket_usage(dto=dto)

    assert isinstance(result, bool)
    assert result is False


def test_get_promotion_then_return_list_for_promotion_entity(
    session, create_users, promotion_factory
):
    promotion = promotion_factory.build(
        promotion_houses=True, promotion_usage_count=True
    )
    session.add(promotion)
    session.commit()

    dto = UseTicketDto(user_id=create_users[0].id, house_id=1)
    result = PaymentRepository().get_promotion(dto=dto)

    assert isinstance(result, PromotionEntity)
    assert result.max_count == 1
    assert result.is_active is True
    assert result.promotion_houses[0].promotion_id == 1
    assert result.promotion_houses[0].house_id == 1
    assert result.promotion_usage_count.usage_count == 1


def test_get_promotion_then_return_none(session, create_users, promotion_factory):
    promotion = promotion_factory.build(is_active=False)
    session.add(promotion)
    session.commit()

    dto = UseTicketDto(user_id=create_users[0].id, house_id=1)
    result = PaymentRepository().get_promotion(dto=dto)

    assert result is None


def test_get_number_of_ticket_then_return_2(session, create_users, ticket_factory):
    tickets = ticket_factory.build_batch(size=2, user_id=1)
    session.add_all(tickets)
    session.commit()

    dto = UseTicketDto(user_id=create_users[0].id, house_id=1)
    result = PaymentRepository().get_number_of_ticket(dto=dto)

    assert result == 2


def test_get_number_of_ticket_then_return_0(session, create_users):
    dto = UseTicketDto(user_id=create_users[0].id, house_id=1)
    result = PaymentRepository().get_number_of_ticket(dto=dto)

    assert result == 0


def test_create_ticket_then_return_ticket_id_is_1(session, create_users):
    dto = CreateUseTicketDto(
        user_id=create_users[0].id,
        type=2,
        amount=1,
        sign=TicketSignEnum.MINUS.value,
        created_by="system",
    )
    result = PaymentRepository().create_ticket(dto=dto)

    assert result == 1


def test_update_ticket_usage_result_then_update_ticket_id(
    session, create_users, ticket_usage_result_factory
):
    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()

    dto = UpdateTicketUsageResultDto(
        user_id=create_users[0].id, public_house_id=1, ticket_id=1
    )
    PaymentRepository().update_ticket_usage_result(dto=dto)

    ticket_usage_result_model = (
        session.query(TicketUsageResultModel)
        .filter(
            TicketUsageResultModel.user_id == dto.user_id,
            TicketUsageResultModel.public_house_id == dto.public_house_id,
        )
        .first()
    )

    assert ticket_usage_result_model.ticket_id == 1


def test_create_promotion_usage_count(session, create_users):
    promotion_id = 1
    dto = UseTicketDto(user_id=create_users[0].id, house_id=1)

    PaymentRepository().create_promotion_usage_count(dto=dto, promotion_id=promotion_id)

    promotion_usage_count_model = (
        session.query(PromotionUsageCountModel)
        .filter(
            PromotionUsageCountModel.promotion_id == promotion_id,
            PromotionUsageCountModel.user_id == dto.user_id,
        )
        .first()
    )

    assert promotion_usage_count_model.usage_count == 1


def test_update_promotion_usage_count(session, create_users):
    promotion_id = 1
    dto = UseTicketDto(user_id=create_users[0].id, house_id=1)

    PaymentRepository().create_promotion_usage_count(dto=dto, promotion_id=promotion_id)
    PaymentRepository().update_promotion_usage_count(dto=dto, promotion_id=promotion_id)

    promotion_usage_count_model = (
        session.query(PromotionUsageCountModel)
        .filter(
            PromotionUsageCountModel.promotion_id == promotion_id,
            PromotionUsageCountModel.user_id == dto.user_id,
        )
        .first()
    )

    assert promotion_usage_count_model.usage_count == 2


def test_create_ticket_target(session, create_users):
    ticket_id = 1
    dto = UseTicketDto(user_id=create_users[0].id, house_id=1)

    PaymentRepository().create_ticket_target(dto=dto, ticket_id=ticket_id)

    result = (
        session.query(TicketTargetModel)
        .filter(
            TicketTargetModel.public_house_id == dto.house_id,
            TicketTargetModel.ticket_id == ticket_id,
        )
        .all()
    )

    assert len(result) == 1
