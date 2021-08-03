import json
from http import HTTPStatus
from unittest.mock import patch

from flask import url_for


def test_get_ticket_usage_result_view_then_return_usage_ticket_list(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
    create_ticket_usage_results,
    public_sale_photo_factory,
):
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)
    session.add(public_sale_photo)
    session.commit()

    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_ticket_usage_result_view"), headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["houses"]) == 1
    assert data["houses"][0]["image_path"] == public_sale_photo.path
    assert "아파트" in data["houses"][0]["name"]


def test_get_ticket_usage_result_view_then_return_no_list(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_real_estate_with_public_sale,
    public_sale_photo_factory,
):
    public_sale_photo = public_sale_photo_factory.build(public_sales_id=1)
    session.add(public_sale_photo)
    session.commit()

    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_ticket_usage_result_view"), headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["houses"]) == 0


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_used_ticket_then_success(
    call_jarvis_analytics_api,
    is_ticket_usage,
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
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

    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(house_id=1)

    with test_request_context:
        response = client.post(
            url_for("api/tanos.use_basic_ticket_view"),
            headers=headers,
            data=json.dumps(dict_),
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["ticket_usage_result"]["message"] == "ticket used"


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_used_promotion_then_success(
    call_jarvis_analytics_api,
    is_ticket_usage,
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    ticket_usage_result_factory,
    ticket_factory,
    promotion_factory,
):
    """
        적용프로모션이 있는 경우
            1. 프로모션 타입 == ALL
            2. 프로모션 횟수가 남아있는 경우 -> 프로모션 사용
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

    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(house_id=1)

    with test_request_context:
        response = client.post(
            url_for("api/tanos.use_basic_ticket_view"),
            headers=headers,
            data=json.dumps(dict_),
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["ticket_usage_result"]["message"] == "promotion used"


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseBasicTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.INTERNAL_SERVER_ERROR,
)
@patch(
    "core.domains.payment.repository.payment_repository.PaymentRepository.is_ticket_usage",
    return_value=False,
)
def test_use_ticket_when_error_on_jarvis_then_failure(
    call_jarvis_analytics_api,
    is_ticket_usage,
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    ticket_usage_result_factory,
    ticket_factory,
):
    """
        티켓 사용시에 jarvis 에서 에러가 발생한 경우
    """
    # data set #############################################################
    ticket_usage_result = ticket_usage_result_factory.build()
    session.add(ticket_usage_result)
    session.commit()

    ticket = ticket_factory.build(user_id=1, ticket_type=False, ticket_targets=False)
    session.add(ticket)
    session.commit()
    ########################################################################

    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(house_id=1)

    with test_request_context:
        response = client.post(
            url_for("api/tanos.use_basic_ticket_view"),
            headers=headers,
            data=json.dumps(dict_),
        )

    data = response.get_json()
    assert response.status_code == 500
    assert data["detail"] == 500
    assert data["message"] == "error on jarvis (usage_charged_ticket)"
