from flask import url_for
from core.domains.report.event.report_enum import SortCompetitionEnum


def test_get_expected_competition_view_then_return_response_schema(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    create_ticket_usage_results,
):
    authorization = make_authorization(user_id=create_users[0].id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_expected_competition_view", house_id=1),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["nickname"] == "noah"
    assert len(data["expected_competitions"]) == len(
        create_ticket_usage_results.predicted_competitions
    )
    assert len(data["sort_competitions"]) == SortCompetitionEnum.LIMIT_NUM.value
