from typing import Union, Optional, List

import inject

from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.banner.dto.banner_dto import GetHomeBannerDto
from core.domains.banner.repository.banner_repository import BannerRepository
from core.domains.house.entity.house_entity import CalendarInfoEntity
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput


class BannerBaseUseCase:
    @inject.autoparams()
    def __init__(self, banner_repo: BannerRepository):
        self._banner_repo = banner_repo


class GetHomeBannerUseCase(BannerBaseUseCase):
    def execute(
            self, dto: GetHomeBannerDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        now = get_server_timestamp()
        year = str(now.year)
        month = str(now.month)

        if 0 < now.month < 10:
            month = "0" + month

        year_month = year + month

        calendar_entities = self.__get_home_screen_calendar_info(year_month=year_month, user_id=dto.user_id)
        banner_list = self._banner_repo.get_banner_list_include_images(section_type=dto.section_type)

    def __get_home_screen_calendar_info(self, year_month: str, user_id: int) -> Optional[List[CalendarInfoEntity]]:
        send_message(topic_name=AuthenticationTopicEnum.CREATE_BLACKLIST, dto=dto)

        return get_event_object(topic_name=AuthenticationTopicEnum.CREATE_BLACKLIST)

class GetPreSubscriptionBannerUseCase(BannerBaseUseCase):
    pass
