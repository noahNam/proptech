from collections import defaultdict
from http import HTTPStatus
from typing import Union, Optional, List

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
from app.persistence.model import PredictedCompetitionModel
from core.domains.house.entity.house_entity import PublicSaleReportEntity, PublicSaleDetailReportEntity
from core.domains.house.enum import HouseTopicEnum
from core.domains.report.dto.report_dto import GetExpectedCompetitionDto, GetSaleInfoDto
from core.domains.report.repository.report_repository import ReportRepository
from core.domains.report.schema.report_schema import (
    GetExpectedCompetitionBaseSchema,
    GetSaleInfoBaseSchema, PublicSaleDetailReportSchema,
)
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

    def _get_public_sale_info(self, house_id: int) -> PublicSaleReportEntity:
        send_message(
            topic_name=HouseTopicEnum.GET_PUBLIC_SALE_INFOS, house_id=house_id,
        )
        return get_event_object(topic_name=HouseTopicEnum.GET_PUBLIC_SALE_INFOS)


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

        # 타입별 총 세대수
        self._calc_total_supply_by_house_type(
            expected_competitions=expected_competitions
        )

        # 유저 닉네임 조회
        user_profile: Optional[UserProfileEntity] = self._get_user_profile(
            user_id=dto.user_id
        )

        result: GetExpectedCompetitionBaseSchema = self._make_response_schema(
            expected_competitions=expected_competitions,
            nickname=user_profile.nickname,
            sort_competitions=sort_competitions,
        )
        return UseCaseSuccessOutput(value=result)

    def _calc_total_supply_by_house_type(
            self, expected_competitions: List[PredictedCompetitionModel]
    ):
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
            c.total_special_supply = calc_special_total_supply.get(
                c.house_structure_type
            )
            c.total_normal_supply = calc_normal_total_supply.get(c.house_structure_type)

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

    def _sort_competition_desc(
            self, expected_competitions: List[PredictedCompetitionModel]
    ) -> List[dict]:
        sort_competitions = list()
        sort_competition_types = list()
        sort_house_structure_types = list()

        # 각 경쟁률을 포함한 list 생성
        for c in expected_competitions:
            sort_house_structure_types: List[str] = sort_house_structure_types + [
                c.house_structure_type for _ in expected_competitions
            ]
            sort_competition_types: List[str] = sort_competition_types + [
                "다자녀",
                "신혼부부",
                "노부모부양",
                "생애최초",
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
                    sort_competition_types[i], sort_competition_types[i + 1] = (
                        sort_competition_types[i + 1],
                        sort_competition_types[i],
                    )
                    last_swap = i

            end = last_swap

        sorted_result = list()
        for idx, _ in enumerate(sort_competitions):
            if idx == 3:
                break

            sorted_result.append(
                dict(
                    competitions=sort_competitions[idx],
                    house_structure_types=sort_house_structure_types[idx],
                    competition_types=sort_competition_types[idx],
                )
            )
        return sorted_result


class GetSaleInfoUseCase(ReportBaseUseCase):
    def execute(
            self, dto: GetSaleInfoDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        report_public_sale_infos: PublicSaleReportEntity = self._get_public_sale_info(house_id=dto.house_id)

        result: GetSaleInfoBaseSchema = self._make_response_schema(
            report_public_sale_infos
        )

        return UseCaseSuccessOutput(value=result)

    def _make_response_schema(
            self, report_public_sale_infos: PublicSaleReportEntity,
    ) -> GetSaleInfoBaseSchema:
        return GetSaleInfoBaseSchema(sale_infos=report_public_sale_infos, )
