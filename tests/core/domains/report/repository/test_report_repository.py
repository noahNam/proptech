from typing import List, Optional

from core.domains.report.entity.report_entity import (
    PredictedCompetitionEntity,
    TicketUsageResultEntity,
)
from core.domains.report.repository.report_repository import ReportRepository


def test_get_expected_competition_then_return_ticket_usage_result_entity(
    session, create_ticket_usage_results
):
    user_id, house_id = 1, 1
    result: Optional[
        TicketUsageResultEntity
    ] = ReportRepository().get_ticket_usage_result_of_house(
        user_id=user_id, house_id=house_id
    )

    assert isinstance(result, TicketUsageResultEntity)


def test_get_expected_competition_then_return_none(session):
    user_id, house_id = 1, 1
    result: Optional[
        TicketUsageResultEntity
    ] = ReportRepository().get_ticket_usage_result_of_house(
        user_id=user_id, house_id=house_id
    )

    assert not result
