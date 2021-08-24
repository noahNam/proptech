from http import HTTPStatus
from typing import Union, Optional, List

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
from app.persistence.model import PredictedCompetitionModel
from core.domains.report.dto.report_dto import GetExpectedCompetitionDto
from core.domains.report.repository.report_repository import ReportRepository
from core.domains.report.schema.report_schema import GetExpectedCompetitionBaseSchema
from core.domains.user.entity.user_entity import UserProfileEntity
from core.domains.user.enum import UserTopicEnum
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class ReportBaseUseCase:
    @inject.autoparams()
    def __init__(self, report_repo: ReportRepository):
        self._report_repo = report_repo

    def _get_user_profile(self, user_id: int) -> Optional[UserProfileEntity]:
        send_message(
            topic_name=UserTopicEnum.GET_USER_PROFILE, user_id=user_id,
        )
        return get_event_object(topic_name=UserTopicEnum.GET_USER_PROFILE)


class GetExpectedCompetitionUseCase(ReportBaseUseCase):
    def execute(
        self, dto: GetExpectedCompetitionDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # 타입별 예측 경쟁률 조회
        expected_competitions: List[
            PredictedCompetitionModel
        ] = self._report_repo.get_expected_competition(
            user_id=dto.user_id, house_id=dto.house_id
        )

        # 타입별 경쟁률
        sort_competitions: List[dict] = self._sort_competition_desc(
            expected_competitions=expected_competitions
        )

        # 유저 닉네임 조회
        user_profile: Optional[UserProfileEntity] = self._get_user_profile(
            user_id=dto.user_id
        )

        result = self._make_response_schema(
            expected_competitions=expected_competitions,
            nickname=user_profile.nickname,
            sort_competitions=sort_competitions,
        )
        return UseCaseSuccessOutput(value=result)

    def _sort_competition_desc(
        self, expected_competitions: List[PredictedCompetitionModel]
    ) -> List[dict]:
        sort_competitions = list()
        sort_house_structure_types = list()

        # 각 경쟁률을 포함한 list 생성
        for c in expected_competitions:
            sort_house_structure_types: List[str] = sort_house_structure_types + [
                c.house_structure_type for _ in expected_competitions
            ]

            sort_competitions: List[int] = sort_competitions + [
                c.multiple_children_competition,
                c.newly_marry_competition,
                c.old_parent_competition,
                c.first_life_competition,
            ]

        # 경쟁률 버블정렬
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
        return sorted_result

    def _make_response_schema(
        self,
        expected_competitions: List[PredictedCompetitionModel],
        nickname: str,
        sort_competitions: List[dict],
    ) -> GetExpectedCompetitionBaseSchema:
        return GetExpectedCompetitionBaseSchema(
            nickname=nickname,
            expected_competitions=expected_competitions,
            sort_competitions=sort_competitions,
        )
