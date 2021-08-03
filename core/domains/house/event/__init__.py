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


pub.subscribe(
    get_public_sales_of_ticket_usage, HouseTopicEnum.GET_PUBLIC_SALES_TO_TICKET_USAGE
)
