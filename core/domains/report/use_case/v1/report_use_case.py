from collections import defaultdict
from datetime import datetime
from http import HTTPStatus
from typing import Union, Optional, List

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.entity.house_entity import PublicSaleReportEntity
from core.domains.house.enum import HouseTopicEnum
from core.domains.report.dto.report_dto import (
    GetExpectedCompetitionDto,
    GetSaleInfoDto,
    GetRecentlySaleDto, ReportUserDto,
)
from core.domains.report.entity.report_entity import PredictedCompetitionEntity, SurveyResultEntity
from core.domains.report.repository.report_repository import ReportRepository
from core.domains.report.schema.report_schema import (
    GetExpectedCompetitionBaseSchema,
    GetRecentlySaleResponseSchema,
    VicinityPublicSaleReportSchema,
    GetSaleInfoResponseSchema, GetUserSurveysResponseSchema, GetSurveysUserReportSchema,
)
from core.domains.user.entity.user_entity import UserProfileEntity
from core.domains.user.enum import UserTopicEnum
from core.domains.user.enum.user_enum import UserSurveyStepEnum
from core.domains.user.enum.user_info_enum import CodeEnum
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
            topic_name=HouseTopicEnum.GET_PUBLIC_SALE_INFO, house_id=house_id,
        )
        return get_event_object(topic_name=HouseTopicEnum.GET_PUBLIC_SALE_INFO)

    def _get_recently_public_sale_info(self, si_gun_gu: str) -> PublicSaleReportEntity:
        send_message(
            topic_name=HouseTopicEnum.GET_RECENTLY_PUBLIC_SALE_INFO,
            si_gun_gu=si_gun_gu,
        )
        return get_event_object(topic_name=HouseTopicEnum.GET_RECENTLY_PUBLIC_SALE_INFO)


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
            PredictedCompetitionEntity
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
            self, expected_competitions: List[PredictedCompetitionEntity]
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
            expected_competitions: List[PredictedCompetitionEntity],
            nickname: str,
            sort_competitions: List[dict],
    ) -> GetExpectedCompetitionBaseSchema:
        return GetExpectedCompetitionBaseSchema(
            nickname=nickname,
            expected_competitions=expected_competitions,
            sort_competitions=sort_competitions,
        )

    def _sort_competition_desc(
            self, expected_competitions: List[PredictedCompetitionEntity]
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

        report_public_sale_info: PublicSaleReportEntity = self._get_public_sale_info(
            house_id=dto.house_id
        )

        # 근처 가장 최근 청약정보
        report_recently_public_sale_info: PublicSaleReportEntity = self._get_recently_public_sale_info(
            si_gun_gu=report_public_sale_info.real_estates.si_gun_gu
        )

        result: GetSaleInfoResponseSchema = self._make_response_schema(
            report_public_sale_info, report_recently_public_sale_info
        )

        return UseCaseSuccessOutput(value=result)

    def _make_response_schema(
            self,
            report_public_sale_info: PublicSaleReportEntity,
            report_recently_public_sale_info: PublicSaleReportEntity,
    ) -> GetSaleInfoResponseSchema:
        report_recently_public_sale_info = VicinityPublicSaleReportSchema(
            id=report_recently_public_sale_info.id,
            name=report_recently_public_sale_info.name,
            supply_household=report_recently_public_sale_info.supply_household,
            si_gun_gu=report_recently_public_sale_info.real_estates.si_gun_gu,
            jibun_address=report_recently_public_sale_info.real_estates.jibun_address,
            latitude=report_recently_public_sale_info.real_estates.latitude,
            longitude=report_recently_public_sale_info.real_estates.longitude,
        )

        return GetSaleInfoResponseSchema(
            sale_info=report_public_sale_info,
            recently_sale_info=report_recently_public_sale_info,
        )


class GetRecentlySaleUseCase(ReportBaseUseCase):
    def execute(
            self, dto: GetRecentlySaleDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        report_recently_public_sale_info: PublicSaleReportEntity = self._get_public_sale_info(
            house_id=dto.house_id
        )

        result: GetRecentlySaleResponseSchema = self._make_response_schema(
            report_recently_public_sale_info
        )

        return UseCaseSuccessOutput(value=result)

    def _make_response_schema(
            self, report_recently_public_sale_info: PublicSaleReportEntity,
    ) -> GetRecentlySaleResponseSchema:
        return GetRecentlySaleResponseSchema(
            recently_sale_info=report_recently_public_sale_info,
        )


class GetUserSurveysUseCase(ReportBaseUseCase):
    def execute(
            self, dto: ReportUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        user_profile: Optional[UserProfileEntity] = self._get_user_profile(
            user_id=dto.user_id
        )

        if not user_profile:
            return UseCaseFailureOutput(
                type="survey_result",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        # 유저분석 티켓 사용 유무
        is_ticket_usage_for_user: bool = self._report_repo.is_ticket_usage_for_user(user_id=dto.user_id)

        survey_result, age = None, None
        if user_profile.survey_step == UserSurveyStepEnum.STEP_COMPLETE.value:
            survey_result: Optional[SurveyResultEntity] = self._report_repo.get_user_survey_results(
                user_id=dto.user_id
            )

        for user_info in user_profile.user_infos:
            if user_info.code == CodeEnum.BIRTHDAY.value:
                age = self._calc_age(birthday=user_info.user_value)
                break

        result = self._make_response_schema(user_profile=user_profile, age=age, survey_result=survey_result, is_ticket_usage_for_user=is_ticket_usage_for_user)

        return UseCaseSuccessOutput(
            value=result
        )

    def _make_response_schema(
            self, user_profile: UserProfileEntity, age: Optional[int], survey_result: Optional[SurveyResultEntity], is_ticket_usage_for_user: bool
    ) -> GetUserSurveysResponseSchema:
        get_surveys_user_report_schema = GetSurveysUserReportSchema(
            is_ticket_usage_for_user=is_ticket_usage_for_user,
            survey_step=user_profile.survey_step,
            nickname=user_profile.nickname,
            age=age
        )

        return GetUserSurveysResponseSchema(
            user=get_surveys_user_report_schema,
            survey_result=survey_result
        )

    def _calc_age(self, birthday: str) -> int:
        # 생일로 나이 계산
        birth = datetime.strptime(birthday, "%Y%m%d")
        today = get_server_timestamp()

        return today.year - birth.year
