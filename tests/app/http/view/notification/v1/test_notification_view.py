import json
from flask import url_for

from core.domains.notification.enum.notification_enum import NotificationHistoryCategoryEnum, NotificationBadgeTypeEnum


def test_get_notification_view_then_two_message(
        client, session, test_request_context, make_header, make_authorization, create_users, create_notifications
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(category=NotificationHistoryCategoryEnum.MY.value)

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_notification_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["messages"]) == 2
    assert data["messages"][0]["category"] == dict_.get("category")
    assert data["messages"][1]["category"] == dict_.get("category")


def test_get_notification_view_then_no_message(
        client, session, test_request_context, make_header, make_authorization, create_users, create_notifications
):
    user_id = create_users[1].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(category=NotificationHistoryCategoryEnum.MY.value)

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_notification_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert len(data["messages"]) == 0


def test_get_badge_view_then_return_true(
        client, session, test_request_context, make_header, make_authorization, create_users, create_notifications
):
    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(badge_type=NotificationBadgeTypeEnum.ALL.value)

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_badge_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] is True


def test_get_badge_view_then_return_fasle(
        client, session, test_request_context, make_header, make_authorization, create_users, create_notifications
):
    user_id = create_users[1].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    dict_ = dict(badge_type=NotificationBadgeTypeEnum.ALL.value)

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_badge_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] is False


def test_update_notification_view_then_return_success(
        client, session, test_request_context, make_header, make_authorization, create_users, create_notifications
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
            url_for("api/tanos.update_notification_view", notification_id=create_notifications[0].id),
            headers=headers,
        )

    dict_ = dict(category=NotificationHistoryCategoryEnum.MY.value)
    with test_request_context:
        response2 = client.get(
            url_for("api/tanos.get_notification_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data1 = response1.get_json()["data"]
    assert response1.status_code == 200
    assert data1["result"] == "success"

    data2 = response2.get_json()["data"]
    assert response2.status_code == 200
    assert data2["messages"][0]["is_read"] is True
