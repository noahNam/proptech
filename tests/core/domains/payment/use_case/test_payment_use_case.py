from core.domains.payment.dto.payment_dto import PaymentUserDto
from core.domains.payment.use_case.v1.payment_use_case import (
    GetTicketUsageResultUseCase,
)
from core.use_case_output import UseCaseSuccessOutput


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
