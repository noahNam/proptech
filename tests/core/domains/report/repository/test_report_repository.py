from collections import defaultdict
from typing import List

from app.persistence.model import PredictedCompetitionModel
from core.domains.report.entity.report_entity import PredictedCompetitionEntity
from core.domains.report.repository.report_repository import ReportRepository


def test_get_expected_competition_then_return_ticket_usage_result_entity(
    session, create_ticket_usage_results
):
    user_id, house_id = 1, 1
    result: List[
        PredictedCompetitionModel
    ] = ReportRepository().get_expected_competition(user_id=user_id, house_id=house_id)

    assert isinstance(result, List)
    assert len(result) == len(create_ticket_usage_results.predicted_competitions)


def test_get_expected_competition_then_return_none(session):
    user_id, house_id = 1, 1
    result: List[
        PredictedCompetitionModel
    ] = ReportRepository().get_expected_competition(user_id=user_id, house_id=house_id)

    assert not result
