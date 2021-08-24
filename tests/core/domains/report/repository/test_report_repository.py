from core.domains.report.entity.report_entity import TicketUsageResultEntity
from core.domains.report.repository.report_repository import ReportRepository


def test_get_expected_competition_then_return_ticket_usage_result_entity(
    session, create_ticket_usage_results
):
    user_id, house_id = 1, 1
    result: TicketUsageResultEntity = ReportRepository().get_expected_competition(
        user_id=user_id, house_id=house_id
    )

    assert isinstance(result, TicketUsageResultEntity)
    assert len(result.predicted_competitions) == len(
        create_ticket_usage_results.predicted_competitions
    )


def test_get_expected_competition_then_return_none(session):
    user_id, house_id = 1, 1
    result: TicketUsageResultEntity = ReportRepository().get_expected_competition(
        user_id=user_id, house_id=house_id
    )

    assert result is None
