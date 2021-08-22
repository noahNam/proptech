import json
from http import HTTPStatus
from unittest.mock import patch

from flask import url_for

from app.persistence.model import RecommendCodeModel, TicketModel
from core.domains.payment.dto.payment_dto import PaymentUserDto
from core.domains.payment.enum.payment_enum import (
    TicketSignEnum,
    TicketTypeDivisionEnum,
)
from core.domains.payment.use_case.v1.payment_use_case import CreateRecommendCodeUseCase
from core.domains.user.enum.user_enum import UserSurveyStepEnum


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
    "core.domains.payment.use_case.v1.payment_use_case.UseHouseTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseHouseTicketUseCase._is_ticket_usage_for_house",
    return_value=False,
)
@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseHouseTicketUseCase._get_user_survey_step",
    return_value=UserSurveyStepEnum.STEP_COMPLETE,
)
def test_use_ticket_when_used_ticket_then_success(
    _call_jarvis_analytics_api,
    _is_ticket_usage_for_house,
    _get_user_survey_step,
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

    ticket = ticket_factory.build(user_id=1, ticket_targets=False)
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
            url_for("api/tanos.use_house_ticket_view"),
            headers=headers,
            data=json.dumps(dict_),
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["ticket_usage_result"]["message"] == "ticket used"


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseHouseTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.OK,
)
@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseHouseTicketUseCase._is_ticket_usage_for_house",
    return_value=False,
)
@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseHouseTicketUseCase._get_user_survey_step",
    return_value=UserSurveyStepEnum.STEP_COMPLETE,
)
def test_use_ticket_when_used_promotion_then_success(
    _call_jarvis_analytics_api,
    _is_ticket_usage_for_house,
    _get_user_survey_step,
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

    ticket = ticket_factory.build(user_id=1, ticket_targets=False)
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
            url_for("api/tanos.use_house_ticket_view"),
            headers=headers,
            data=json.dumps(dict_),
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["ticket_usage_result"]["message"] == "promotion used"


@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseHouseTicketUseCase._call_jarvis_analytics_api",
    return_value=HTTPStatus.INTERNAL_SERVER_ERROR,
)
@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseHouseTicketUseCase._is_ticket_usage_for_house",
    return_value=False,
)
@patch(
    "core.domains.payment.use_case.v1.payment_use_case.UseHouseTicketUseCase._get_user_survey_step",
    return_value=UserSurveyStepEnum.STEP_COMPLETE,
)
def test_use_ticket_when_error_on_jarvis_then_failure(
    _call_jarvis_analytics_api,
    _is_ticket_usage_for_house,
    _get_user_survey_step,
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

    ticket = ticket_factory.build(user_id=1, ticket_targets=False)
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
            url_for("api/tanos.use_house_ticket_view"),
            headers=headers,
            data=json.dumps(dict_),
        )

    data = response.get_json()
    assert response.status_code == 500
    assert data["detail"] == 500
    assert data["message"] == "error on jarvis (usage_charged_ticket)"


def test_create_recommend_code_view_then_return_recommend_code(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
):
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.post(
            url_for("api/tanos.create_recommend_code_view"), headers=headers,
        )

    # data 검증 #############################################################
    recommend_code = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == create_users[0].id)
        .first()
    )
    ########################################################################

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["recommend_code"]) == 7
    assert (
        data["recommend_code"] == str(recommend_code.code_group) + recommend_code.code
    )


def test_get_recommend_code_view_then_success(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    recommend_code_factory,
):
    # 쿠폰 제공자 set
    recommend_code = recommend_code_factory.build(
        user_id=create_users[0].id, is_used=False, code_count=0
    )
    session.add(recommend_code)
    session.commit()

    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_recommend_code_view"), headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["recommend_code"]) == 7
    assert (
        data["recommend_code"] == str(recommend_code.code_group) + recommend_code.code
    )


def test_get_recommend_code_view_then_failure(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
):
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_recommend_code_view"), headers=headers,
        )

    data = response.get_json()
    assert data["detail"] == "recommend code"
    assert data["message"] == "not_found_error"


def test_use_recommend_code_view_then_success(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    recommend_code_factory,
):
    # 쿠폰 제공자 set
    recommend_code = recommend_code_factory.build(
        user_id=create_users[0].id, is_used=False, code_count=0
    )
    session.add(recommend_code)
    session.commit()

    authorization = make_authorization(user_id=create_users[1].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    full_code = str(recommend_code.code_group) + recommend_code.code
    with test_request_context:
        response = client.post(
            url_for("api/tanos.use_recommend_code_view", code=full_code),
            headers=headers,
        )

    # data 검증 #############################################################
    # 무료쿠폰 제공자
    provider_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == create_users[0].id)
        .first()
    )

    # 무료쿠폰 사용자
    receiver_user = (
        session.query(RecommendCodeModel)
        .filter(RecommendCodeModel.user_id == create_users[1].id)
        .first()
    )

    # 티켓 히스토리
    receiver_ticket = (
        session.query(TicketModel)
        .filter(TicketModel.user_id == create_users[1].id)
        .first()
    )
    ########################################################################

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

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


def test_use_recommend_code_view_when_user_already_used_code_then_failure(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    recommend_code_factory,
):
    """
        추천코드 입력하는 유저가 이미 추천 코드를 입력한 유저
    """
    # 쿠폰 제공자, 수신자 set
    payment_provider_dto = PaymentUserDto(user_id=create_users[0].id)
    CreateRecommendCodeUseCase().execute(dto=payment_provider_dto)

    recommend_code = recommend_code_factory.build(
        user_id=create_users[1].id, is_used=True
    )
    session.add(recommend_code)
    session.commit()

    authorization = make_authorization(user_id=create_users[1].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    full_code = str(recommend_code.code_group) + recommend_code.code
    with test_request_context:
        response = client.post(
            url_for("api/tanos.use_recommend_code_view", code=full_code),
            headers=headers,
        )

    data = response.get_json()
    assert response.status_code == 400
    assert data["detail"] == "user already used code"
    assert data["message"] == "invalid_request_error"


def test_use_recommend_code_view_when_when_code_does_not_exist_user_already_used_code_then_failure(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
):
    """
        존재하지 않는 추천 코드를 입력한 경우
    """
    # 쿠폰 제공자 set
    payment_provider_dto = PaymentUserDto(user_id=create_users[0].id)
    CreateRecommendCodeUseCase().execute(dto=payment_provider_dto)

    authorization = make_authorization(user_id=create_users[1].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    full_code = "0ABCDEF"
    with test_request_context:
        response = client.post(
            url_for("api/tanos.use_recommend_code_view", code=full_code),
            headers=headers,
        )

    data = response.get_json()
    assert response.status_code == 404
    assert data["detail"] == "code does not exist"
    assert data["message"] == "not_found_error"


def test_use_recommend_code_view_when_when_code_already_been_all_used_then_failure(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    recommend_code_factory,
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

    authorization = make_authorization(user_id=create_users[1].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    full_code = str(recommend_code.code_group) + recommend_code.code
    with test_request_context:
        response = client.post(
            url_for("api/tanos.use_recommend_code_view", code=full_code),
            headers=headers,
        )

    data = response.get_json()
    assert response.status_code == 400
    assert data["detail"] == "code already been all used"
    assert data["message"] == "invalid_request_error"
