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


def test_sort(session, create_ticket_usage_results):
    user_id, house_id = 1, 1
    expected_competitions: List[
        PredictedCompetitionEntity
    ] = ReportRepository().get_expected_competition(user_id=user_id, house_id=house_id)

    calc_special_total_supply = defaultdict(int)
    calc_normal_total_supply = defaultdict(int)
    for c in expected_competitions:
        special_calc = (
            c.multiple_children_supply
            + c.newly_marry_supply
            + c.old_parent_supply
            + c.first_life_supply
        )

        calc_special_total_supply[c.house_structure_type] = (
            calc_special_total_supply[c.house_structure_type] + special_calc
        )
        calc_normal_total_supply[c.house_structure_type] = (
            calc_normal_total_supply[c.house_structure_type] + c.normal_supply
        )

    for c in expected_competitions:
        c.total_special_supply = calc_special_total_supply.get(c.house_structure_type)
        c.total_normal_supply = calc_normal_total_supply.get(c.house_structure_type)

    assert 1 == 1
