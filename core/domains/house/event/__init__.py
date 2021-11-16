from typing import List

from flask import g
from pubsub import pub

from core.domains.house.entity.house_entity import (
    GetPublicSaleOfTicketUsageEntity,
    PublicSaleReportEntity,
)
from core.domains.house.enum import HouseTopicEnum
from core.domains.house.repository.house_repository import HouseRepository


def get_public_sales_of_ticket_usage(public_house_ids: int,):
    result: List[
        GetPublicSaleOfTicketUsageEntity
    ] = HouseRepository().get_public_sales_of_ticket_usage(
        public_house_ids=public_house_ids
    )
    setattr(g, HouseTopicEnum.GET_PUBLIC_SALES_TO_TICKET_USAGE, result)


def get_public_sale_info(house_id: int,):
    result: PublicSaleReportEntity = HouseRepository().get_public_sale_info(
        house_id=house_id
    )
    setattr(g, HouseTopicEnum.GET_PUBLIC_SALE_INFO, result)


def get_recently_public_sale_info(report_public_sale_infos: PublicSaleReportEntity,):
    result: PublicSaleReportEntity = HouseRepository().get_recently_public_sale_info(
        report_public_sale_infos=report_public_sale_infos
    )
    setattr(g, HouseTopicEnum.GET_RECENTLY_PUBLIC_SALE_INFO, result)


pub.subscribe(
    get_public_sales_of_ticket_usage, HouseTopicEnum.GET_PUBLIC_SALES_TO_TICKET_USAGE
)
pub.subscribe(get_public_sale_info, HouseTopicEnum.GET_PUBLIC_SALE_INFO)
pub.subscribe(
    get_recently_public_sale_info, HouseTopicEnum.GET_RECENTLY_PUBLIC_SALE_INFO
)
