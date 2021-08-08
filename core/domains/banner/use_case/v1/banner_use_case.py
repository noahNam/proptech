from http import HTTPStatus
from typing import Union, Optional, List

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.banner.dto.banner_dto import GetHomeBannerDto, SectionTypeDto
from core.domains.banner.enum.banner_enum import SectionType
from core.domains.banner.repository.banner_repository import BannerRepository
from core.domains.house.entity.house_entity import CalendarInfoEntity
from core.domains.house.enum import HouseTopicEnum
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class BannerBaseUseCase:
    @inject.autoparams()
    def __init__(self, banner_repo: BannerRepository):
        self._banner_repo = banner_repo


class GetHomeBannerUseCase(BannerBaseUseCase):
    def execute(
        self, dto: GetHomeBannerDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if dto.section_type != SectionType.HOME_SCREEN.value:
            return UseCaseFailureOutput(
                type="section_type",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )
        now = get_server_timestamp()
        year = str(now.year)
        month = str(now.month)

        if 0 < now.month < 10:
            month = "0" + month

        year_month = year + month

        calendar_entities = self.__get_home_screen_calendar_info(
            year_month=year_month, user_id=dto.user_id
        )
        banner_list = self._banner_repo.get_banner_list_include_images(
            section_type=dto.section_type
        )
        result = self._banner_repo.make_home_banner_entity(
            banner_list=banner_list, calendar_entities=calendar_entities
        )

        return UseCaseSuccessOutput(value=result)

    def __get_home_screen_calendar_info(
        self, year_month: str, user_id: int
    ) -> List[CalendarInfoEntity]:
        send_message(
            topic_name=HouseTopicEnum.GET_HOME_SCREEN_CALENDAR_INFO,
            year_month=year_month,
            user_id=user_id,
        )

        return get_event_object(topic_name=HouseTopicEnum.GET_HOME_SCREEN_CALENDAR_INFO)


class GetPreSubscriptionBannerUseCase(BannerBaseUseCase):
    def execute(
        self, dto: SectionTypeDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if dto.section_type != SectionType.PRE_SUBSCRIPTION_INFO.value:
            return UseCaseFailureOutput(
                type="section_type",
                message=FailureType.INVALID_REQUEST_ERROR,
                code=HTTPStatus.BAD_REQUEST,
            )
        banner_list = self._banner_repo.get_banner_list_include_images(
            section_type=dto.section_type
        )
        button_links = self._banner_repo.get_button_link_list(
            section_type=dto.section_type
        )
        result = self._banner_repo.make_pre_subscription_banner_entity(
            banner_list=banner_list, button_links=button_links
        )
        return UseCaseSuccessOutput(value=result)
