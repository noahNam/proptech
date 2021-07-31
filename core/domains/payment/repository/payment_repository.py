from typing import Optional, List

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.persistence.model import TicketUsageResultModel
from core.domains.payment.dto.payment_dto import PaymentUserDto

logger = logger_.getLogger(__name__)


class PaymentRepository:
    """
        house 도메인에서 payment 도메인으로 쪼개면서 주석처리
    """

    # def get_ticket_usage_results(
    #         self, dto: PaymentUserDto
    # ) -> List[GetTicketUsageResultEntity]:
    #     subquery = (
    #         session.query(TicketUsageResultModel.public_house_id)
    #             .filter_by(user_id=dto.user_id, is_active=True)
    #             .subquery()
    #     )
    #
    #     query = (
    #         session.query(PublicSaleModel)
    #             .options(joinedload(PublicSaleModel.public_sale_photos))
    #             .filter(PublicSaleModel.id == subquery.c.public_house_id)
    #     )
    #
    #     query_set = query.all()
    #     return self._make_get_ticket_usage_result_entity(query_set=query_set)

    def get_ticket_usage_results(self, dto: PaymentUserDto) -> List[int]:
        query = session.query(TicketUsageResultModel).filter_by(
            user_id=dto.user_id, is_active=True
        )
        public_houses = query.all()

        if not public_houses:
            return []
        return [public_house.id for public_house in public_houses]
