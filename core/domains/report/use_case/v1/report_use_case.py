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
    GetRecentlySaleDto,
    ReportUserDto,
)
from core.domains.report.entity.report_entity import (
    PredictedCompetitionEntity,
    SurveyResultEntity,
    UserAnalysisEntity,
    UserAnalysisCategoryEntity,
    TicketUsageResultEntity,
    HouseTypeRankEntity,
)
from core.domains.report.enum.report_enum import UserAnalysisFormatText, RegionEnum
from core.domains.report.repository.report_repository import ReportRepository
from core.domains.report.schema.report_schema import (
    GetExpectedCompetitionBaseSchema,
    GetRecentlySaleResponseSchema,
    VicinityPublicSaleReportSchema,
    GetSaleInfoResponseSchema,
    GetUserSurveysResponseSchema,
    GetSurveysUserReportSchema,
    GetSurveysResultBaseSchema,
)
from core.domains.user.dto.user_dto import AvgMonthlyIncomeWokrerDto
from core.domains.user.entity.user_entity import UserProfileEntity, SidoCodeEntity
from core.domains.user.enum import UserTopicEnum
from core.domains.user.enum.user_enum import UserSurveyStepEnum
from core.domains.user.enum.user_info_enum import (
    CodeEnum,
    IsHouseHolderCodeEnum,
    IsHouseOwnerCodeEnum,
    IsSubAccountEnum,
    AssetsRealEstateEnum,
    AssetsCarEnum,
    AssetsTotalEnum,
)
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

    def _get_sido_name(self, sido_id: int, sigugun_id: int) -> SidoCodeEntity:
        send_message(
            topic_name=UserTopicEnum.GET_SIDO_NAME,
            sido_id=sido_id,
            sigugun_id=sigugun_id,
        )
        return get_event_object(topic_name=UserTopicEnum.GET_SIDO_NAME)

    def _get_avg_monthly_income_workers(self) -> AvgMonthlyIncomeWokrerDto:
        send_message(topic_name=UserTopicEnum.GET_AVG_MONTHLY_INCOME_WORKERS,)
        return get_event_object(topic_name=UserTopicEnum.GET_AVG_MONTHLY_INCOME_WORKERS)

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
        ticket_usage_results: Optional[
            TicketUsageResultEntity
        ] = self._report_repo.get_ticket_usage_result_of_house(
            user_id=dto.user_id, house_id=dto.house_id
        )

        # 순서 정렬 (1.낮은 전용면적 + 알파벳순, 2. 해당지역,기타경기,기타지역 순)
        self._sort_expected_competitions_by_type_and_region(
            expected_competitions=ticket_usage_results.predicted_competitions
        )

        # 타입별 경쟁률
        # 직접 계산하는 방식에서 Jarvis 계산 방식으로 바뀜
        # sort_competitions: List[dict] = self._sort_competition_desc(
        #     expected_competitions=expected_competitions
        # )
        self._sort_predicted_competition(
            house_type_ranks=ticket_usage_results.house_type_ranks
        )

        # 타입별 총 세대수
        self._calc_total_supply_by_house_type(
            expected_competitions=ticket_usage_results.predicted_competitions
        )

        # 유저 닉네임 조회
        user_profile: Optional[UserProfileEntity] = self._get_user_profile(
            user_id=dto.user_id
        )

        result: GetExpectedCompetitionBaseSchema = self._make_response_schema(
            predicted_competitions=ticket_usage_results.predicted_competitions,
            nickname=user_profile.nickname if user_profile else None,
            house_type_ranks=ticket_usage_results.house_type_ranks,
        )
        return UseCaseSuccessOutput(value=result)

    def _make_response_schema(
        self,
        predicted_competitions: List[PredictedCompetitionEntity],
        nickname: Optional[str],
        house_type_ranks: List[HouseTypeRankEntity],
    ) -> GetExpectedCompetitionBaseSchema:

        return GetExpectedCompetitionBaseSchema(
            nickname=nickname,
            predicted_competitions=predicted_competitions,
            house_type_ranks=house_type_ranks,
        )

    def _calc_total_supply_by_house_type(
        self, expected_competitions: List[PredictedCompetitionEntity]
    ):
        calc_special_total_supply = defaultdict(int)
        calc_normal_total_supply = defaultdict(int)

        for c in expected_competitions:
            multiple_children_supply = (
                0 if not c.multiple_children_supply else c.multiple_children_supply
            )
            newly_marry_supply = 0 if not c.newly_marry_supply else c.newly_marry_supply
            old_parent_supply = 0 if not c.old_parent_supply else c.old_parent_supply
            first_life_supply = 0 if not c.first_life_supply else c.first_life_supply
            normal_supply = 0 if not c.normal_supply else c.normal_supply

            special_calc = (
                multiple_children_supply
                + newly_marry_supply
                + old_parent_supply
                + first_life_supply
            )

            calc_special_total_supply[c.house_structure_type] = (
                calc_special_total_supply[c.house_structure_type] + special_calc
            )
            calc_normal_total_supply[c.house_structure_type] = (
                calc_normal_total_supply[c.house_structure_type] + normal_supply
            )
        for c in expected_competitions:
            c.total_special_supply = calc_special_total_supply.get(
                c.house_structure_type
            )
            c.total_normal_supply = calc_normal_total_supply.get(c.house_structure_type)

    def _sort_predicted_competition(
        self, house_type_ranks: List[HouseTypeRankEntity]
    ) -> None:
        end = len(house_type_ranks) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                if house_type_ranks[i].rank > house_type_ranks[i + 1].rank:
                    house_type_ranks[i], house_type_ranks[i + 1] = (
                        house_type_ranks[i + 1],
                        house_type_ranks[i],
                    )
                    last_swap = i
            end = last_swap

    def _sort_expected_competitions_by_type_and_region(
        self, expected_competitions: List[PredictedCompetitionEntity]
    ) -> None:
        sort_dict = {
            RegionEnum.THE_AREA.value: 0,
            RegionEnum.OTHER_GYEONGGI.value: 1,
            RegionEnum.OTHER_REGION.value: 2,
        }
        end = len(expected_competitions) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                if (
                    expected_competitions[i].house_structure_type
                    > expected_competitions[i + 1].house_structure_type
                ):
                    expected_competitions[i], expected_competitions[i + 1] = (
                        expected_competitions[i + 1],
                        expected_competitions[i],
                    )
                    last_swap = i
            end = last_swap

        end = len(expected_competitions) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                if expected_competitions[
                    i
                ].house_structure_type == expected_competitions[
                    i + 1
                ].house_structure_type and sort_dict.get(
                    expected_competitions[i].region
                ) > sort_dict.get(
                    expected_competitions[i + 1].region
                ):
                    expected_competitions[i], expected_competitions[i + 1] = (
                        expected_competitions[i + 1],
                        expected_competitions[i],
                    )
                    last_swap = i
            end = last_swap

    def _sort_competition_desc(
        self, expected_competitions: List[PredictedCompetitionEntity]
    ) -> List[dict]:
        sort_competitions = list()
        sort_competition_types = list()
        sort_house_structure_types = list()

        # 각 경쟁률을 포함한 list 생성
        sort_competition_list = ["다자녀", "신혼부부", "노부모부양", "생애최초", "일반"]
        for c in expected_competitions:
            sort_house_structure_types: List[str] = sort_house_structure_types + [
                c.house_structure_type for _ in range(len(sort_competition_list))
            ]
            sort_competition_types: List[
                str
            ] = sort_competition_types + sort_competition_list
            sort_competitions: List[int] = sort_competitions + [
                c.multiple_children_competition,
                c.newly_marry_competition,
                c.old_parent_competition,
                c.first_life_competition,
                c.normal_competition,
            ]

        # 경쟁률 버블정렬
        end = len(sort_competitions) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                # 예측 경쟁률이 None일 경우, 지원 불가한 경우
                sort_competitions[i] = (
                    9999999 if not sort_competitions[i] else sort_competitions[i]
                )
                sort_competitions[i + 1] = (
                    9999999
                    if not sort_competitions[i + 1]
                    else sort_competitions[i + 1]
                )

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

            # 예측 경쟁률이 None일 경우, 지원 불가한 경우
            sort_competitions[idx] = (
                None if sort_competitions[idx] == 9999999 else sort_competitions[idx]
            )
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


class GetUserReportUseCase(ReportBaseUseCase):
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

        # 유저 설문 데이터 맵핑
        user_infos: List[GetSurveysResultBaseSchema] = self._make_user_info_object(
            user_profile=user_profile
        )

        # 유저분석 티켓 사용 유무
        is_ticket_usage_for_user: bool = self._report_repo.is_ticket_usage_for_user(
            user_id=dto.user_id
        )

        # 변수 초기화
        (
            survey_result,
            age,
            user_analyses,
            user_analysis_category,
            analysis_text,
            analysis_text_dict,
        ) = (None, None, list(), None, None, defaultdict(list))

        # 유저 설문 분석 결과 조회
        if (
            user_profile.survey_step == UserSurveyStepEnum.STEP_COMPLETE.value
            or user_profile.survey_step == UserSurveyStepEnum.STEP_TWO.value
        ):
            survey_result: Optional[
                SurveyResultEntity
            ] = self._report_repo.get_user_survey_results(user_id=dto.user_id)

        # 유저별 category 유형 조회
        if is_ticket_usage_for_user:
            user_analyses: List[
                UserAnalysisEntity
            ] = self._report_repo.get_user_analysis(user_id=dto.user_id)

        # 유저별 category 분석 메세지 조회
        for user_analysis in user_analyses:
            user_analysis_categories: List[
                UserAnalysisCategoryEntity
            ] = self._report_repo.get_user_analysis_category_text(
                category=user_analysis.category, div=user_analysis.div
            )

            # 유저별 category 분석 메세지 formatting
            user_info_dict = dict()
            for user_info in user_profile.user_infos:
                if user_info.code == CodeEnum.SUB_ACCOUNT_TOTAL_PRICE.value:
                    user_info_dict.setdefault(
                        "sub_account_total_price",
                        format(int(user_info.user_value), ",d"),
                    )
                elif user_info.code == CodeEnum.IS_CHILD.value:
                    user_info_dict.setdefault("child_num", 0)
                    if int(user_info.user_value) < 4:
                        user_info_dict.update({"child_num": user_info.user_value})

            user_variable_change_dict = {
                UserAnalysisFormatText.NICKNAME.value: user_profile.nickname,
                UserAnalysisFormatText.SUB_POINT.value: survey_result.total_point,
                UserAnalysisFormatText.SUB_ACCOUNT_TOTAL_AMT.value: user_info_dict.get(
                    "sub_account_total_price"
                ),
                UserAnalysisFormatText.CHILD_NUM.value: user_info_dict.get("child_num"),
            }

            # response formatting
            for user_analysis_category in user_analysis_categories:
                analysis_text_list = [
                    user_analysis_category.seq,
                    user_analysis_category.type,
                ]

                if user_analysis_category.user_analysis_category_detail:
                    format_text = user_analysis_category.user_analysis_category_detail.format_text.split(
                        ","
                    )
                    for idx, text in enumerate(format_text):
                        format_text[idx] = user_variable_change_dict.get(text)

                    analysis_text = user_analysis_category.output_text.format(
                        *format_text
                    )
                    analysis_text_list.append(analysis_text)

                    analysis_text_dict[user_analysis_category.title].append(
                        analysis_text_list
                    )
                    continue

                analysis_text_list.append(user_analysis_category.output_text)
                analysis_text_dict[user_analysis_category.title].append(
                    analysis_text_list
                )

        # 생일 계산
        for user_info in user_profile.user_infos:
            if user_info.code == CodeEnum.BIRTHDAY.value:
                age = self._calc_age(birthday=user_info.user_value)
                break

        result = self._make_response_schema(
            user_profile=user_profile,
            age=age,
            survey_result=survey_result,
            is_ticket_usage_for_user=is_ticket_usage_for_user,
            analysis_text_dict=analysis_text_dict,
            user_infos=user_infos,
        )

        return UseCaseSuccessOutput(value=result)

    def _make_user_info_object(
        self, user_profile: UserProfileEntity
    ) -> List[GetSurveysResultBaseSchema]:
        result = list()
        code_dict = {
            # subjective = 주관식 변수 또는 바인딩 필요한 코드(거주지, 월소득)
            CodeEnum.NICKNAME.value: "subjective",
            CodeEnum.BIRTHDAY.value: "subjective",
            # 주택 소유 여부
            CodeEnum.IS_HOUSE_OWNER.value: dict(
                zip(
                    IsHouseOwnerCodeEnum.COND_CD.value,
                    IsHouseOwnerCodeEnum.COND_NM.value,
                )
            ),
            # 세대주 여부
            CodeEnum.IS_HOUSE_HOLDER.value: dict(
                zip(
                    IsHouseHolderCodeEnum.COND_CD.value,
                    IsHouseHolderCodeEnum.COND_NM.value,
                )
            ),
            # 주소
            CodeEnum.ADDRESS.value: "subjective",
            CodeEnum.ADDRESS_DETAIL.value: "subjective",
            CodeEnum.ADDRESS_DATE.value: "subjective",
            # 청약통장
            CodeEnum.IS_SUB_ACCOUNT.value: dict(
                zip(IsSubAccountEnum.COND_CD.value, IsSubAccountEnum.COND_NM.value)
            ),
            CodeEnum.SUB_ACCOUNT_TIMES.value: "subjective",
            CodeEnum.SUB_ACCOUNT_TOTAL_PRICE.value: "subjective",
            # 자산
            CodeEnum.ASSETS_REAL_ESTATE.value: dict(
                zip(
                    AssetsRealEstateEnum.COND_CD.value,
                    AssetsRealEstateEnum.COND_NM.value,
                )
            ),
            CodeEnum.ASSETS_CAR.value: dict(
                zip(AssetsCarEnum.COND_CD.value, AssetsCarEnum.COND_NM.value)
            ),
            CodeEnum.ASSETS_TOTAL.value: dict(
                zip(AssetsTotalEnum.COND_CD.value, AssetsTotalEnum.COND_NM.value)
            ),
        }

        # 주소 맵핑 변수 초기화
        address_cnt, address_dict = 0, dict()

        for user_info in user_profile.user_infos:
            if value := code_dict.get(user_info.code):
                if value != "subjective":
                    value = (
                        None
                        if not user_info.user_value
                        else value.get(int(user_info.user_value))
                    )
                else:
                    value = user_info.user_value

                if (
                    user_info.code == CodeEnum.ADDRESS.value
                    or user_info.code == CodeEnum.ADDRESS_DETAIL.value
                ):
                    # 주소 맵핑
                    address_cnt += 1
                    address_dict[user_info.code] = user_info.user_value
                else:
                    base_schema = GetSurveysResultBaseSchema(
                        code=user_info.code, value=value
                    )
                    result.append(base_schema)

        if address_cnt == 2:
            sido_entity: SidoCodeEntity = self._get_sido_name(
                sido_id=int(address_dict.get(CodeEnum.ADDRESS.value)),
                sigugun_id=int(address_dict.get(CodeEnum.ADDRESS_DETAIL.value)),
            )
            address_schema = GetSurveysResultBaseSchema(
                code=CodeEnum.ADDRESS.value, value=sido_entity.sido_name
            )
            address_detail_schema = GetSurveysResultBaseSchema(
                code=CodeEnum.ADDRESS_DETAIL.value, value=sido_entity.sigugun_name
            )
            result.extend([address_schema, address_detail_schema])

        return result

    def _make_response_schema(
        self,
        user_profile: UserProfileEntity,
        age: Optional[int],
        survey_result: Optional[SurveyResultEntity],
        is_ticket_usage_for_user: bool,
        analysis_text_dict: dict,
        user_infos: List[GetSurveysResultBaseSchema],
    ) -> GetUserSurveysResponseSchema:
        get_surveys_user_report_schema = GetSurveysUserReportSchema(
            is_ticket_usage_for_user=is_ticket_usage_for_user,
            survey_step=user_profile.survey_step,
            nickname=user_profile.nickname,
            age=age,
        )

        return GetUserSurveysResponseSchema(
            user=get_surveys_user_report_schema,
            survey_result=survey_result,
            analysis_text=analysis_text_dict,
            user_infos=user_infos,
        )

    def _calc_age(self, birthday: str) -> int:
        # 생일로 나이 계산
        birth = datetime.strptime(birthday, "%Y%m%d")
        today = get_server_timestamp()

        return today.year - birth.year
