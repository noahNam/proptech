from http import HTTPStatus
from typing import Union, List

import inject

from app.extensions.utils.event_observer import send_message, get_event_object
from core.domains.house.entity.house_entity import GetPublicSaleOfTicketUsageEntity
from core.domains.house.enum import HouseTopicEnum
from core.domains.payment.dto.payment_dto import PaymentUserDto
from core.domains.payment.repository.payment_repository import PaymentRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType


class PaymentBaseUseCase:
    @inject.autoparams()
    def __init__(self, payment_repo: PaymentRepository):
        self._payment_repo = payment_repo


class GetTicketUsageResultUseCase(PaymentBaseUseCase):
    def execute(
        self, dto: PaymentUserDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        public_house_ids: List[int] = self._payment_repo.get_ticket_usage_results(
            dto=dto
        )
        result = list()
        if public_house_ids:
            result: List[
                GetPublicSaleOfTicketUsageEntity
            ] = self._get_public_sales_of_ticket_usage(
                public_house_ids=public_house_ids
            )

        return UseCaseSuccessOutput(value=result)

    def _get_public_sales_of_ticket_usage(
        self, public_house_ids: List[int]
    ) -> List[GetPublicSaleOfTicketUsageEntity]:
        send_message(
            topic_name=HouseTopicEnum.GET_PUBLIC_SALES_TO_TICKET_USAGE,
            public_house_ids=public_house_ids,
        )
        return get_event_object(
            topic_name=HouseTopicEnum.GET_PUBLIC_SALES_TO_TICKET_USAGE
        )
