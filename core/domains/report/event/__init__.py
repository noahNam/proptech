from typing import List, Optional

from flask import g
from pubsub import pub

from core.domains.report.entity.report_entity import TicketUsageResultEntity
from core.domains.report.enum import ReportTopicEnum
from core.domains.report.repository.report_repository import ReportRepository


def get_ticket_usage_results(user_id: int, type_: str):
    ticket_usage_result_ids: List[
        TicketUsageResultEntity
    ] = ReportRepository().get_ticket_usage_results(user_id=user_id, type_=type_)

    setattr(g, ReportTopicEnum.GET_TICKET_USAGE_RESULTS, ticket_usage_result_ids)


def is_ticket_usage_for_house(user_id: int, house_id: int):
    result: bool = ReportRepository().is_ticket_usage_for_house(
        user_id=user_id, house_id=house_id
    )

    setattr(g, ReportTopicEnum.IS_TICKET_USAGE_FOR_HOUSE, result)


def is_ticket_usage_for_user(user_id: int,):
    result: bool = ReportRepository().is_ticket_usage_for_user(user_id=user_id,)

    setattr(g, ReportTopicEnum.IS_TICKET_USAGE_FOR_USER, result)


def update_ticket_usage_result(user_id: int, house_id: Optional[int], ticket_id: int):
    ReportRepository().update_ticket_usage_result(
        user_id=user_id, public_house_id=house_id, ticket_id=ticket_id
    )

    setattr(g, ReportTopicEnum.UPDATE_TICKET_USAGE_RESULT, None)


pub.subscribe(get_ticket_usage_results, ReportTopicEnum.GET_TICKET_USAGE_RESULTS)
pub.subscribe(is_ticket_usage_for_house, ReportTopicEnum.IS_TICKET_USAGE_FOR_HOUSE)
pub.subscribe(is_ticket_usage_for_user, ReportTopicEnum.IS_TICKET_USAGE_FOR_USER)
pub.subscribe(update_ticket_usage_result, ReportTopicEnum.UPDATE_TICKET_USAGE_RESULT)
