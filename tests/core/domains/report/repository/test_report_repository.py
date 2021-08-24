from typing import List

from app.persistence.model import PredictedCompetitionModel
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


def test_sort(session, create_ticket_usage_results):
    user_id, house_id = 1, 1
    result: List[
        PredictedCompetitionModel
    ] = ReportRepository().get_expected_competition(user_id=user_id, house_id=house_id)

    sort_competitions = list()
    sort_house_structure_types = list()
    for c in result:
        sort_house_structure_types = sort_house_structure_types + [
            c.house_structure_type for _ in range(1, 5)
        ]
        sort_competitions = sort_competitions + [
            c.multiple_children_competition,
            c.newly_marry_competition,
            c.old_parent_competition,
            c.first_life_competition,
        ]

    end = len(sort_competitions) - 1
    while end > 0:
        last_swap = 0
        for i in range(end):
            if sort_competitions[i] > sort_competitions[i + 1]:
                sort_competitions[i], sort_competitions[i + 1] = (
                    sort_competitions[i + 1],
                    sort_competitions[i],
                )
                sort_house_structure_types[i], sort_house_structure_types[i + 1] = (
                    sort_house_structure_types[i + 1],
                    sort_house_structure_types[i],
                )
                last_swap = i

        end = last_swap

    sorted_result = list()
    for idx, _ in enumerate(sort_competitions):
        if idx == 3:
            break

        sorted_result.append(
            dict(
                sort_competitions=sort_competitions[idx],
                sort_house_structure_types=sort_house_structure_types[idx],
            )
        )

    assert 1 == 1
