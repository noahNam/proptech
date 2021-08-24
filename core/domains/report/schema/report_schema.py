from typing import List

from pydantic import BaseModel, StrictStr, StrictInt

from core.domains.report.entity.report_entity import PredictedCompetitionEntity


class SortCompetitionBaseSchema(BaseModel):
    sort_competitions: StrictInt
    sort_house_structure_types: StrictStr


class GetExpectedCompetitionBaseSchema(BaseModel):
    nickname: StrictStr
    expected_competitions: List[PredictedCompetitionEntity]
    sort_competitions: List[SortCompetitionBaseSchema]


class GetExpectedCompetitionResponseSchema(BaseModel):
    result: GetExpectedCompetitionBaseSchema
