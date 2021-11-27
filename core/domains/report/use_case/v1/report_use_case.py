import re
from collections import defaultdict
from datetime import datetime
from http import HTTPStatus
from typing import Union, Optional, List, Dict

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
from app.extensions.utils.house_helper import HouseHelper
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.banner.entity.banner_entity import BannerEntity, BannerImageEntity
from core.domains.banner.enum import BannerTopicEnum
from core.domains.house.entity.house_entity import (
    PublicSaleReportEntity,
    PublicSaleDetailReportEntity,
)
from core.domains.house.enum import HouseTopicEnum
from core.domains.house.enum.house_enum import SectionType
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
    PublicSaleReportSchema,
    PublicSaleDetailReportSchema,
    RecentlySaleReportSchema,
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

    def _get_recently_public_sale_info(
        self, report_public_sale_infos: PublicSaleReportEntity
    ) -> PublicSaleReportEntity:
        send_message(
            topic_name=HouseTopicEnum.GET_RECENTLY_PUBLIC_SALE_INFO,
            report_public_sale_infos=report_public_sale_infos,
        )
        return get_event_object(topic_name=HouseTopicEnum.GET_RECENTLY_PUBLIC_SALE_INFO)

    def _sort_domain_list_to_region(self, target_list: List):
        sort_dict = {
            RegionEnum.THE_AREA.value: 0,
            RegionEnum.OTHER_GYEONGGI.value: 1,
            RegionEnum.OTHER_REGION.value: 2,
        }

        for target_domain in target_list:
            end = len(target_domain) - 1
            while end > 0:
                last_swap = 0
                for i in range(end):
                    if sort_dict.get(target_domain[i]["region"]) > sort_dict.get(
                        target_domain[i + 1]["region"]
                    ):
                        target_domain[i], target_domain[i + 1] = (
                            target_domain[i + 1],
                            target_domain[i],
                        )
                        last_swap = i
                end = last_swap

    def _convert_area_type_dict(self, convert_target_dict: Dict, key_name: str) -> Dict:
        result_dict = dict()

        domain_list = list(convert_target_dict.keys())
        for domain in domain_list:
            convert_dict = dict()
            domain_target_dict = convert_target_dict.get(domain)
            key_list = list(convert_target_dict.get(domain).keys())
            for key in key_list:
                domain_target = domain_target_dict.get(key)
                area_type = domain_target.get(key_name)
                if re.search("\d", area_type):
                    new_key = re.sub(r"[^0-9]", "", area_type)
                    convert_dict.setdefault(new_key, []).append(
                        domain_target_dict.get(key)
                    )
                else:
                    convert_dict.setdefault(key, []).append(domain_target_dict.get(key))

            result_dict.setdefault(domain, dict()).update(convert_dict)

        return result_dict

    def _sort_area_type_by_dict(self, convert_target_dict: Dict, key_name: str) -> None:
        key_list = convert_target_dict.keys()
        for key in key_list:
            area_type_dict = convert_target_dict.get(key)
            area_type_keys = area_type_dict.keys()

            for area_type_key in area_type_keys:
                area_type_list = area_type_dict.get(area_type_key)
                end = len(area_type_list) - 1
                while end > 0:
                    last_swap = 0
                    for i in range(end):
                        # 102A, 84A str로 비교시 84A가 크기 때문에 숫자로 재비교
                        number1 = "".join(
                            re.findall("\d+", area_type_list[i].get(key_name))[0]
                        )
                        number2 = "".join(
                            re.findall("\d+", area_type_list[i + 1].get(key_name))[0]
                        )

                        if int(number1) > int(number2):
                            area_type_list[i], area_type_list[i + 1] = (
                                area_type_list[i + 1],
                                area_type_list[i],
                            )
                            last_swap = i
                    end = last_swap

                end = len(area_type_list) - 1
                while end > 0:
                    last_swap = 0
                    for i in range(end):
                        # 위의 숫자기반 정렬을 알파벳 순으로 다시 재정렬
                        word1 = "".join(
                            re.findall("[a-zA-Z]+", area_type_list[i].get(key_name))
                        )
                        word2 = "".join(
                            re.findall("[a-zA-Z]+", area_type_list[i + 1].get(key_name))
                        )

                        number1 = "".join(
                            re.findall("\d+", area_type_list[i].get(key_name))[0]
                        )
                        number2 = "".join(
                            re.findall("\d+", area_type_list[i + 1].get(key_name))[0]
                        )

                        if (number1 == number2) and (word1 > word2):
                            area_type_list[i], area_type_list[i + 1] = (
                                area_type_list[i + 1],
                                area_type_list[i],
                            )
                            last_swap = i
                    end = last_swap


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
        predicted_competition_dict: Dict = self._make_response_object_to_predicted_competitions(
            expected_competitions=ticket_usage_results.predicted_competitions
        )

        HouseHelper().sort_predicted_competition(
            house_type_ranks=ticket_usage_results.house_type_ranks
        )

        # 타입별 총 세대수
        # self._calc_total_supply_by_house_type(
        #     expected_competitions=ticket_usage_results.predicted_competitions
        # )

        # 유저 닉네임 조회
        user_profile: Optional[UserProfileEntity] = self._get_user_profile(
            user_id=dto.user_id
        )

        # 토드홈의 경쟁률 얼마나 정확할까? 배너 조회
        section_type = SectionType.PREDICT_COMPETITION.value
        banner_list = self._get_banner_list(section_type=section_type)

        result: GetExpectedCompetitionBaseSchema = self._make_response_schema(
            predicted_competitions=predicted_competition_dict,
            nickname=user_profile.nickname if user_profile else None,
            house_type_ranks=ticket_usage_results.house_type_ranks,
            banner_image=banner_list[0].banner_image if banner_list else None,
        )
        return UseCaseSuccessOutput(value=result)

    def _make_response_object_to_predicted_competitions(
        self, expected_competitions: List[PredictedCompetitionEntity],
    ) -> Dict:
        (
            domain_marry_list,
            domain_first_life_list,
            domain_children_list,
            domain_old_parent_list,
            domain_normal_list,
        ) = (list(), list(), list(), list(), list())
        (
            domain_marry_dict,
            domain_first_life_dict,
            domain_children_dict,
            domain_old_parent_dict,
            domain_normal_dict,
        ) = (dict(), dict(), dict(), dict(), dict())

        for expected_competition in expected_competitions:
            domain_common_dict = dict(
                region=expected_competition.region,
                region_percentage=expected_competition.region_percentage,
            )
            marry_dict = dict(
                competition=expected_competition.newly_marry_competition,
                supply=expected_competition.newly_marry_supply,
                passing_score=None,
            )
            first_life_dict = dict(
                competition=expected_competition.first_life_competition,
                supply=expected_competition.first_life_supply,
                passing_score=None,
            )
            children_dict = dict(
                competition=expected_competition.multiple_children_competition,
                supply=expected_competition.multiple_children_supply,
                passing_score=None,
            )
            old_parent_dict = dict(
                competition=expected_competition.old_parent_competition,
                supply=expected_competition.old_parent_supply,
                passing_score=None,
            )
            normal_dict = dict(
                competition=expected_competition.normal_competition,
                supply=expected_competition.normal_supply,
                passing_score=expected_competition.normal_passing_score,
            )

            marry_dict.update(domain_common_dict)
            first_life_dict.update(domain_common_dict)
            children_dict.update(domain_common_dict)
            old_parent_dict.update(domain_common_dict)
            normal_dict.update(domain_common_dict)

            if domain_marry_dict.get(expected_competition.private_area):
                domain_marry_list.append(marry_dict)
                domain_first_life_list.append(first_life_dict)
                domain_children_list.append(children_dict)
                domain_old_parent_list.append(old_parent_dict)
                domain_normal_list.append(normal_dict)
            else:
                domain_marry_list = [marry_dict]
                domain_first_life_list = [first_life_dict]
                domain_children_list = [children_dict]
                domain_old_parent_list = [old_parent_dict]
                domain_normal_list = [normal_dict]

            # 각 타입별 마지막 지역(해당지역,기타경기,기타지역)이 들어오면 지역순서대로 정렬
            if len(domain_marry_list) >= 2:
                self._sort_domain_list_to_region(
                    target_list=[
                        domain_marry_list,
                        domain_first_life_list,
                        domain_children_list,
                        domain_old_parent_list,
                        domain_normal_list,
                    ]
                )

            domain_marry_dict.setdefault(
                expected_competition.private_area, dict()
            ).update(
                house_structure_type=expected_competition.house_structure_type,
                infos=domain_marry_list,
            )
            domain_first_life_dict.setdefault(
                expected_competition.private_area, dict()
            ).update(
                house_structure_type=expected_competition.house_structure_type,
                infos=domain_first_life_list,
            )
            domain_children_dict.setdefault(
                expected_competition.private_area, dict()
            ).update(
                house_structure_type=expected_competition.house_structure_type,
                infos=domain_children_list,
            )
            domain_old_parent_dict.setdefault(
                expected_competition.private_area, dict()
            ).update(
                house_structure_type=expected_competition.house_structure_type,
                infos=domain_old_parent_list,
            )
            domain_normal_dict.setdefault(
                expected_competition.private_area, dict()
            ).update(
                house_structure_type=expected_competition.house_structure_type,
                infos=domain_normal_list,
            )

        convert_target_dict = dict(
            marry=domain_marry_dict,
            first_life=domain_first_life_dict,
            children=domain_children_dict,
            old_parent=domain_old_parent_dict,
            normal=domain_normal_dict,
        )

        predicted_competition_dict: Dict = self._convert_area_type_dict(
            convert_target_dict=convert_target_dict, key_name="house_structure_type",
        )
        return predicted_competition_dict

    def _make_response_schema(
        self,
        predicted_competitions: Dict,
        nickname: Optional[str],
        house_type_ranks: List[HouseTypeRankEntity],
        banner_image: Optional[BannerImageEntity],
    ) -> GetExpectedCompetitionBaseSchema:

        return GetExpectedCompetitionBaseSchema(
            nickname=nickname,
            predicted_competitions=predicted_competitions,
            house_type_ranks=house_type_ranks,
            banner=banner_image.path if banner_image else None,
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

    def _sort_expected_competitions_by_type_and_region(
        self, expected_competitions: List[PredictedCompetitionEntity]
    ) -> None:
        end = len(expected_competitions) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                # private_area로 최초 정렬
                number1 = expected_competitions[i].private_area
                number2 = expected_competitions[i + 1].private_area

                if int(number1) > int(number2):
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
                word1 = "".join(
                    re.findall(
                        "[a-zA-Z]+", expected_competitions[i].house_structure_type
                    )
                )
                word2 = "".join(
                    re.findall(
                        "[a-zA-Z]+", expected_competitions[i + 1].house_structure_type
                    )
                )

                number1 = "".join(
                    re.findall("\d+", expected_competitions[i].house_structure_type)[0]
                )
                number2 = "".join(
                    re.findall(
                        "\d+", expected_competitions[i + 1].house_structure_type
                    )[0]
                )

                if (number1 == number2) and (word1 > word2):
                    expected_competitions[i], expected_competitions[i + 1] = (
                        expected_competitions[i + 1],
                        expected_competitions[i],
                    )
                    last_swap = i
            end = last_swap

    def _get_banner_list(self, section_type: int) -> List[BannerEntity]:
        send_message(
            topic_name=BannerTopicEnum.GET_BANNER_LIST, section_type=section_type
        )
        return get_event_object(topic_name=BannerTopicEnum.GET_BANNER_LIST)


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

        report_public_sale_infos: PublicSaleReportEntity = self._get_public_sale_info(
            house_id=dto.house_id
        )

        # 근처 가장 최근 청약정보
        report_recently_public_sale_info: PublicSaleReportEntity = self._get_recently_public_sale_info(
            report_public_sale_infos=report_public_sale_infos
        )

        # 기획변경으로 인한 response entity 변경 -> entity object 생성
        public_sale_detail_dict: dict = self._make_response_object_to_report_public_sale_info(
            report_public_sale_infos=report_public_sale_infos
        )

        result: GetSaleInfoResponseSchema = self._make_response_schema(
            report_public_sale_infos,
            report_recently_public_sale_info,
            public_sale_detail_dict,
        )

        return UseCaseSuccessOutput(value=result)

    def _make_response_object_to_report_public_sale_info(
        self, report_public_sale_infos: PublicSaleReportEntity,
    ) -> dict:

        public_sale_details: List[
            PublicSaleDetailReportEntity
        ] = report_public_sale_infos.public_sale_details

        end = len(public_sale_details) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                # 102A, 84A str로 비교시 84A가 크기 때문에 숫자로 재비교
                number1 = "".join(
                    re.findall("\d+", public_sale_details[i].area_type)[0]
                )
                number2 = "".join(
                    re.findall("\d+", public_sale_details[i + 1].area_type)[0]
                )

                if int(number1) > int(number2):
                    public_sale_details[i], public_sale_details[i + 1] = (
                        public_sale_details[i + 1],
                        public_sale_details[i],
                    )
                    last_swap = i
            end = last_swap

        end = len(public_sale_details) - 1
        while end > 0:
            last_swap = 0
            for i in range(end):
                # 위의 숫자기반 정렬을 알파벳 순으로 다시 재정렬
                word1 = "".join(
                    re.findall("[a-zA-Z]+", public_sale_details[i].area_type)
                )
                word2 = "".join(
                    re.findall("[a-zA-Z]+", public_sale_details[i + 1].area_type)
                )

                number1 = "".join(
                    re.findall("\d+", public_sale_details[i].area_type)[0]
                )
                number2 = "".join(
                    re.findall("\d+", public_sale_details[i + 1].area_type)[0]
                )

                if (number1 == number2) and (word1 > word2):
                    public_sale_details[i], public_sale_details[i + 1] = (
                        public_sale_details[i + 1],
                        public_sale_details[i],
                    )
                    last_swap = i
            end = last_swap

        public_sale_detail_dict = dict()
        for public_sale_detail in public_sale_details:
            area_type = "".join(re.findall("\d+", public_sale_detail.area_type)[0])

            public_sale_detail_report_schema = PublicSaleDetailReportSchema(
                area_type=public_sale_detail.area_type,
                private_area=public_sale_detail.private_area,
                supply_area=public_sale_detail.supply_area,
                supply_price=public_sale_detail.supply_price,
                special_household=public_sale_detail.special_household,
                multi_children_household=public_sale_detail.multi_children_household,
                newlywed_household=public_sale_detail.newlywed_household,
                old_parent_household=public_sale_detail.old_parent_household,
                first_life_household=public_sale_detail.first_life_household,
                general_household=public_sale_detail.general_household,
                total_household=public_sale_detail.total_household,
                price_per_meter=public_sale_detail.price_per_meter,
                pyoung_number=public_sale_detail.pyoung_number,
                public_sale_detail_photo=public_sale_detail.public_sale_detail_photo,
            )

            public_sale_detail_dict.setdefault(area_type, []).append(
                public_sale_detail_report_schema
            )

        return public_sale_detail_dict

    def _make_response_schema(
        self,
        report_public_sale_infos: PublicSaleReportEntity,
        report_recently_public_sale_info: PublicSaleReportEntity,
        public_sale_detail_dict: dict,
    ) -> GetSaleInfoResponseSchema:
        recently_sale_info_schema = VicinityPublicSaleReportSchema(
            id=report_recently_public_sale_info.id,
            name=report_recently_public_sale_info.name,
            supply_household=report_recently_public_sale_info.supply_household,
            si_gun_gu=report_recently_public_sale_info.real_estates.si_gun_gu,
            jibun_address=report_recently_public_sale_info.real_estates.jibun_address,
            latitude=report_recently_public_sale_info.real_estates.latitude,
            longitude=report_recently_public_sale_info.real_estates.longitude,
        )

        public_sale_photos = None
        if report_public_sale_infos.public_sale_photos:
            report_public_sale_infos.public_sale_photos.sort(
                key=lambda obj: obj.seq, reverse=False
            )
            public_sale_photos = [
                public_sale_photo.path
                for public_sale_photo in report_public_sale_infos.public_sale_photos
            ]

        public_sale_report_schema = PublicSaleReportSchema(
            supply_household=report_public_sale_infos.supply_household,
            offer_date=report_public_sale_infos.offer_date,
            special_supply_date=report_public_sale_infos.special_supply_date,
            special_supply_etc_date=report_public_sale_infos.special_supply_etc_date,
            special_etc_gyeonggi_date=report_public_sale_infos.special_etc_gyeonggi_date,
            first_supply_date=report_public_sale_infos.first_supply_date,
            first_supply_etc_date=report_public_sale_infos.first_supply_etc_date,
            first_etc_gyeonggi_date=report_public_sale_infos.first_etc_gyeonggi_date,
            second_supply_date=report_public_sale_infos.second_supply_date,
            second_supply_etc_date=report_public_sale_infos.second_supply_etc_date,
            second_etc_gyeonggi_date=report_public_sale_infos.second_etc_gyeonggi_date,
            notice_winner_date=report_public_sale_infos.notice_winner_date,
            public_sale_photos=public_sale_photos,
            public_sale_details=public_sale_detail_dict,
            real_estates=report_public_sale_infos.real_estates,
        )

        return GetSaleInfoResponseSchema(
            sale_info=public_sale_report_schema,
            recently_sale_info=recently_sale_info_schema,
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

        house_applicants_dict: Dict = self._make_response_object_to_house_applicants(
            report_recently_public_sale_info=report_recently_public_sale_info
        )
        public_sale_detail_dict: Dict = self._make_response_object_to_public_sale_details(
            report_recently_public_sale_info=report_recently_public_sale_info
        )

        result: GetRecentlySaleResponseSchema = self._make_response_schema(
            report_recently_public_sale_info=report_recently_public_sale_info,
            house_applicants_dict=house_applicants_dict,
            public_sale_detail_dict=public_sale_detail_dict,
        )

        return UseCaseSuccessOutput(value=result)

    def _make_response_object_to_public_sale_details(
        self, report_recently_public_sale_info: PublicSaleReportEntity,
    ) -> Dict:
        public_sale_detail_dict = dict()
        public_sale_detail_list = list()

        competitions = report_recently_public_sale_info.public_sale_details
        for competition in competitions:
            key = "{}_{}".format(competition.private_area, competition.supply_area)

            detail_dict = dict(
                area_type=competition.area_type,
                special_household=competition.special_household,
                general_household=competition.general_household,
                total_househlod=competition.total_household,
                price_per_meter=competition.price_per_meter,
                private_area=competition.private_area,
                pyoung_number=competition.pyoung_number,
                supply_area=competition.supply_area,
                supply_price=competition.supply_price,
                public_sale_detail_photo=competition.public_sale_detail_photo,
            )

            if public_sale_detail_dict.get(key):
                public_sale_detail_list.append(detail_dict)
            else:
                public_sale_detail_list = [detail_dict]

            public_sale_detail_dict.setdefault(key, dict()).update(
                detail_dict
            )

        convert_target_dict = dict(public_sale_details=public_sale_detail_dict,)

        result_dict: Dict = self._convert_area_type_dict(
            convert_target_dict=convert_target_dict, key_name="area_type"
        )

        self._sort_area_type_by_dict(
            convert_target_dict=result_dict, key_name="area_type"
        )
        return result_dict

    def _make_response_object_to_house_applicants(
        self, report_recently_public_sale_info: PublicSaleReportEntity,
    ) -> Dict:
        (
            domain_marry_list,
            domain_first_life_list,
            domain_children_list,
            domain_old_parent_list,
            domain_normal_list,
        ) = (list(), list(), list(), list(), list())
        (
            domain_marry_dict,
            domain_first_life_dict,
            domain_children_dict,
            domain_old_parent_dict,
            domain_normal_dict,
        ) = (dict(), dict(), dict(), dict(), dict())

        competitions = report_recently_public_sale_info.public_sale_details
        for competition in competitions:
            key = "{}_{}".format(competition.private_area, competition.supply_area)

            for special_supply_result in competition.special_supply_results:
                domain_common_dict = dict(
                    region=special_supply_result.region,
                    region_percentage=special_supply_result.region_percent,
                )
                marry_dict = dict(
                    competition=None,
                    applicant=special_supply_result.newlywed_vol,
                    score=None,
                )
                first_life_dict = dict(
                    competition=None,
                    applicant=special_supply_result.first_life_vol,
                    score=None,
                )
                children_dict = dict(
                    competition=None,
                    applicant=special_supply_result.multi_children_vol,
                    score=None,
                )
                old_parent_dict = dict(
                    competition=None,
                    applicant=special_supply_result.old_parent_vol,
                    score=None,
                )

                marry_dict.update(domain_common_dict)
                first_life_dict.update(domain_common_dict)
                children_dict.update(domain_common_dict)
                old_parent_dict.update(domain_common_dict)

                if domain_marry_dict.get(key):
                    domain_marry_list.append(marry_dict)
                    domain_first_life_list.append(first_life_dict)
                    domain_children_list.append(children_dict)
                    domain_old_parent_list.append(old_parent_dict)
                else:
                    domain_marry_list = [marry_dict]
                    domain_first_life_list = [first_life_dict]
                    domain_children_list = [children_dict]
                    domain_old_parent_list = [old_parent_dict]

                # 각 타입별 마지막 지역(해당지역,기타경기,기타지역)이 들어오면 지역순서대로 정렬
                if len(domain_marry_list) == 3:
                    self._sort_domain_list_to_region(
                        target_list=[
                            domain_marry_list,
                            domain_first_life_list,
                            domain_children_list,
                            domain_old_parent_list,
                            domain_normal_list,
                        ]
                    )

                domain_marry_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.newlywed_household,
                    infos=domain_marry_list,
                )
                domain_first_life_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.first_life_household,
                    infos=domain_first_life_list,
                )
                domain_children_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.multi_children_household,
                    infos=domain_children_list,
                )
                domain_old_parent_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.old_parent_household,
                    infos=domain_old_parent_list,
                )

            for general_supply_result in competition.general_supply_results:
                domain_common_dict = dict(
                    region=general_supply_result.region,
                    region_percentage=general_supply_result.region_percent,
                )
                normal_dict = dict(
                    competition=general_supply_result.competition_rate,
                    applicant=general_supply_result.applicant_num,
                    score=general_supply_result.win_point,
                )

                normal_dict.update(domain_common_dict)

                if domain_normal_dict.get(key):
                    domain_normal_list.append(normal_dict)
                else:
                    domain_normal_list = [normal_dict]

                domain_normal_dict.setdefault(key, dict()).update(
                    house_structure_type=competition.area_type,
                    supply_household=competition.general_household,
                    infos=domain_normal_list,
                )

        convert_target_dict = dict(
            marry=domain_marry_dict,
            first_life=domain_first_life_dict,
            children=domain_children_dict,
            old_parent=domain_old_parent_dict,
            normal=domain_normal_dict,
        )

        house_applicants_dict: Dict = self._convert_area_type_dict(
            convert_target_dict=convert_target_dict, key_name="house_structure_type"
        )

        self._sort_area_type_by_dict(
            convert_target_dict=house_applicants_dict, key_name="house_structure_type"
        )
        return house_applicants_dict

    def _make_response_schema(
        self,
        report_recently_public_sale_info: PublicSaleReportEntity,
        house_applicants_dict: Dict,
        public_sale_detail_dict: Dict,
    ) -> GetRecentlySaleResponseSchema:
        public_sale_photos = None
        if report_recently_public_sale_info.public_sale_photos:
            report_recently_public_sale_info.public_sale_photos.sort(
                key=lambda obj: obj.seq, reverse=False
            )
            public_sale_photos = [
                public_sale_photo.path
                for public_sale_photo in report_recently_public_sale_info.public_sale_photos
            ]

        recently_sale_info = RecentlySaleReportSchema(
            supply_household=report_recently_public_sale_info.supply_household,
            offer_date=report_recently_public_sale_info.offer_date,
            special_supply_date=report_recently_public_sale_info.special_supply_date,
            special_supply_etc_date=report_recently_public_sale_info.special_supply_etc_date,
            special_etc_gyeonggi_date=report_recently_public_sale_info.special_etc_gyeonggi_date,
            first_supply_date=report_recently_public_sale_info.first_supply_date,
            first_supply_etc_date=report_recently_public_sale_info.first_supply_etc_date,
            first_etc_gyeonggi_date=report_recently_public_sale_info.first_etc_gyeonggi_date,
            second_supply_date=report_recently_public_sale_info.second_supply_date,
            second_supply_etc_date=report_recently_public_sale_info.second_supply_etc_date,
            second_etc_gyeonggi_date=report_recently_public_sale_info.second_etc_gyeonggi_date,
            notice_winner_date=report_recently_public_sale_info.notice_winner_date,
            real_estates=report_recently_public_sale_info.real_estates,
            public_sale_photos=public_sale_photos,
            public_sale_details=public_sale_detail_dict.get("public_sale_details"),
        )
        return GetRecentlySaleResponseSchema(
            recently_sale_info=recently_sale_info,
            house_applicants=house_applicants_dict,
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
