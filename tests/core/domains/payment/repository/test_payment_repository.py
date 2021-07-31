from core.domains.payment.dto.payment_dto import PaymentUserDto
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
