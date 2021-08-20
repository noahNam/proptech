from typing import List

from flask import g
from pubsub import pub

from core.domains.report.enum import ReportTopicEnum
from core.domains.report.repository.report_repository import ReportRepository


def get_ticket_usage_results(user_id: int,):
    ticket_usage_result_ids: List[int] = ReportRepository().get_ticket_usage_results(
        user_id=user_id
    )

    setattr(g, ReportTopicEnum.GET_TICKET_USAGE_RESULTS, ticket_usage_result_ids)


def is_ticket_usage(user_id: int, house_id: int):
    result: bool = ReportRepository().is_ticket_usage(
        user_id=user_id, house_id=house_id
    )

    setattr(g, ReportTopicEnum.IS_TICKET_USAGE, result)


def update_ticket_usage_result(user_id: int, house_id: int, ticket_id: int):
    ReportRepository().update_ticket_usage_result(
        user_id=user_id, public_house_id=house_id, ticket_id=ticket_id
    )

    setattr(g, ReportTopicEnum.IS_TICKET_USAGE, None)


pub.subscribe(get_ticket_usage_results, ReportTopicEnum.GET_TICKET_USAGE_RESULTS)
pub.subscribe(is_ticket_usage, ReportTopicEnum.IS_TICKET_USAGE)
pub.subscribe(update_ticket_usage_result, ReportTopicEnum.UPDATE_TICKET_USAGE_RESULT)
