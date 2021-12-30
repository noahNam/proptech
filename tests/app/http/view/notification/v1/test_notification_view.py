import json

import pytest
from flask import url_for

from app.persistence.model import ReceivePushTypeHistoryModel
from core.domains.notification.enum.notification_enum import (
    NotificationHistoryCategoryEnum,
    NotificationBadgeTypeEnum,
    NotificationPushTypeEnum,
)
from core.domains.notification.use_case.v1.notification_use_case import (
    GetReceiveNotificationSettingUseCase,
)


def test_get_notification_view_then_two_message(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_notifications,
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    category = NotificationHistoryCategoryEnum.MY.value
    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_notification_view", category=category),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["messages"]) == 2
    assert data["messages"][0]["category"] == category
    assert data["messages"][1]["category"] == category


def test_get_notification_view_then_no_message(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_notifications,
):
    user_id = create_users[1].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    category = NotificationHistoryCategoryEnum.MY.value

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_notification_view", category=category),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["messages"]) == 0


def test_get_badge_view_then_return_true(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_notifications,
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for(
                "api/tanos.get_badge_view",
                badge_type=NotificationBadgeTypeEnum.ALL.value,
            ),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] is True


def test_get_badge_view_then_return_false(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_notifications,
):
    user_id = create_users[1].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for(
                "api/tanos.get_badge_view",
                badge_type=NotificationBadgeTypeEnum.ALL.value,
            ),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] is False


@pytest.mark.skip(reason="reader - writer test 관련 skip")
def test_update_notification_view_then_return_success(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_notifications,
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response1 = client.patch(
            url_for(
                "api/tanos.update_notification_view",
                notification_id=create_notifications[0].id,
            ),
            headers=headers,
        )

    with test_request_context:
        response2 = client.get(
            url_for(
                "api/tanos.get_notification_view",
                category=NotificationHistoryCategoryEnum.MY.value,
            ),
            headers=headers,
        )

    data1 = response1.get_json()["data"]
    assert response1.status_code == 200
    assert data1["result"] == "success"

    data2 = response2.get_json()["data"]
    assert response2.status_code == 200
    assert data2["messages"][0]["is_read"] is True


def test_get_receive_notification_settings_view_then_success(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_notifications,
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_receive_notification_settings_view"),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["receive_push_types"]["official"] is True
    assert data["receive_push_types"]["private"] is True
    assert data["receive_push_types"]["marketing"] is True


def test_update_receive_notification_settings_view_when_change_push_type_then_official_is_false(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_notifications,
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )
    dict_ = dict(push_type=NotificationPushTypeEnum.OFFICIAL.value, is_active=False)

    with test_request_context:
        response = client.patch(
            url_for("api/tanos.update_receive_notification_setting_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

    result = GetReceiveNotificationSettingUseCase().execute(user_id=create_users[0].id)
    history_result = (
        session.query(ReceivePushTypeHistoryModel)
        .filter_by(user_id=create_users[0].id)
        .all()
    )

    assert result.value["official"] is False
    assert len(history_result) == 1
