from typing import List

from flask import g
from pubsub import pub

from core.domains.house.entity.house_entity import GetPublicSaleOfTicketUsageEntity
from core.domains.house.enum import HouseTopicEnum
from core.domains.house.repository.house_repository import HouseRepository


def get_public_sales_of_ticket_usage(
    public_house_ids: int,
) -> List[GetPublicSaleOfTicketUsageEntity]:
    result: List[
        GetPublicSaleOfTicketUsageEntity
    ] = HouseRepository().get_public_sales_of_ticket_usage(
        public_house_ids=public_house_ids
    )
    setattr(g, HouseTopicEnum.GET_PUBLIC_SALES_TO_TICKET_USAGE, result)


def get_home_screen_calendar_info(year_month: str, user_id: int):
    search_filters = HouseRepository().get_calendar_info_filters(year_month=year_month)
    calendar_entities = HouseRepository().get_calendar_info(user_id=user_id, search_filters=search_filters)
    setattr(g, HouseTopicEnum.GET_HOME_SCREEN_CALENDAR_INFO, calendar_entities)


pub.subscribe(
    get_public_sales_of_ticket_usage, HouseTopicEnum.GET_PUBLIC_SALES_TO_TICKET_USAGE
)
pub.subscribe(get_home_screen_calendar_info, HouseTopicEnum.GET_HOME_SCREEN_CALENDAR_INFO)
