from typing import List

from core.domains.report.dto.report_dto import GetExpectedCompetitionDto
from core.domains.report.enum.report_enum import SortCompetitionEnum
from core.domains.report.schema.report_schema import GetExpectedCompetitionBaseSchema
from core.domains.report.use_case.v1.report_use_case import (
    GetExpectedCompetitionUseCase,
)
from core.use_case_output import UseCaseSuccessOutput

get_expected_competition_dto = GetExpectedCompetitionDto(user_id=1, house_id=1)


def test_get_expected_competition_use_case_then_return_response_schema(
    session, create_users, create_ticket_usage_results,
):
    result = GetExpectedCompetitionUseCase().execute(dto=get_expected_competition_dto)
    assert isinstance(result, UseCaseSuccessOutput)
    assert isinstance(result.value, GetExpectedCompetitionBaseSchema)
    assert isinstance(result.value.house_type_ranks, List)
    assert len(result.value.house_type_ranks) == 2
    assert isinstance(result.value.house_type_ranks[0].subscription_type, str)
