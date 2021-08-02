from core.domains.payment.dto.payment_dto import PaymentUserDto, UseTicketDto
from core.domains.payment.entity.payment_entity import PromotionEntity
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


def test_get_promotion_then_return_list_for_promotion_entity(
        session,
        create_users,
        promotion_factory
):
    promotion = promotion_factory.build(promotion_houses=True, promotion_usage_count=True)
    session.add(promotion)
    session.commit()

    dto = UseTicketDto(
        user_id=create_users[0].id,
        house_id=1
    )

    result = PaymentRepository().get_promotion(dto=dto)
    assert isinstance(result, PromotionEntity)
    assert result.max_count == 3
    assert result.is_active is True
    assert result.promotion_houses[0].promotion_id == 1
    assert result.promotion_houses[0].house_id == 1
    assert result.promotion_usage_count.usage_count == 0
