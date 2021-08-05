from typing import Optional, List

from sqlalchemy import exc, exists
from sqlalchemy.orm import selectinload
from strgen import StringGenerator

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.persistence.model import (
    TicketUsageResultModel,
    PromotionModel,
    PromotionUsageCountModel,
    TicketModel,
    TicketTargetModel,
    PromotionHouseModel,
    RecommendCodeModel,
)
from core.domains.payment.dto.payment_dto import (
    PaymentUserDto,
    UseTicketDto,
    CreateTicketDto,
    UpdateTicketUsageResultDto,
)
from core.domains.payment.entity.payment_entity import (
    PromotionEntity,
    RecommendCodeEntity,
)
from core.domains.payment.enum.payment_enum import TicketSignEnum
from core.exceptions import NotUniqueErrorException

logger = logger_.getLogger(__name__)


class PaymentRepository:
    def get_ticket_usage_results(self, dto: PaymentUserDto) -> List[int]:
        query = session.query(TicketUsageResultModel).filter_by(
            user_id=dto.user_id, is_active=True
        )
        public_houses = query.all()

        if not public_houses:
            return []
        return [public_house.id for public_house in public_houses]

    def is_ticket_usage(self, dto: UseTicketDto) -> bool:
        return session.query(
            exists()
            .where(TicketUsageResultModel.public_house_id == dto.house_id)
            .where(TicketUsageResultModel.user_id == dto.user_id)
        ).scalar()

    def get_promotion(self, dto: UseTicketDto) -> Optional[PromotionEntity]:
        filters = list()
        filters.append(PromotionModel.is_active == True)

        query = (
            session.query(PromotionModel)
            .join(
                PromotionHouseModel,
                PromotionModel.id == PromotionHouseModel.promotion_id,
                isouter=True,
            )
            .join(
                PromotionUsageCountModel,
                (PromotionModel.id == PromotionUsageCountModel.promotion_id)
                & (PromotionUsageCountModel.user_id == dto.user_id),
                isouter=True,
            )
            .options(selectinload(PromotionModel.promotion_houses))
            .options(selectinload(PromotionModel.promotion_usage_count))
            .filter(*filters)
        )
        promotion = query.first()

        if not promotion:
            return None
        return promotion.to_entity()

    def get_number_of_ticket(self, dto: UseTicketDto) -> int:
        query = session.query(TicketModel).filter_by(user_id=dto.user_id)
        tickets = query.all()
        return self._calc_total_amount(tickets=tickets)

    def _calc_total_amount(self, tickets: List[TicketModel]) -> int:
        total_amount = 0
        if not tickets:
            return total_amount

        for ticket in tickets:
            if ticket.is_active:
                if ticket.sign == TicketSignEnum.PLUS.value:
                    total_amount += ticket.amount
                else:
                    total_amount -= ticket.amount

        return 0 if total_amount < 0 else total_amount

    def create_ticket(self, dto: CreateTicketDto) -> int:
        try:
            ticket = TicketModel(
                user_id=dto.user_id,
                type=dto.type,
                amount=dto.amount,
                sign=dto.sign,
                is_active=True,
                created_by=dto.created_by,
            )

            session.add(ticket)
            session.commit()

            return ticket.id
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[PaymentRepository][create_ticket] user_id : {dto.user_id}, error : {e}"
            )
            raise NotUniqueErrorException(type_="T100")

    def update_ticket_usage_result(self, dto: UpdateTicketUsageResultDto) -> None:
        try:
            filters = list()
            filters.append(TicketUsageResultModel.user_id == dto.user_id)
            filters.append(
                TicketUsageResultModel.public_house_id == dto.public_house_id
            )

            session.query(TicketUsageResultModel).filter(*filters).update(
                {"ticket_id": dto.ticket_id}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[PaymentRepository][update_ticket_usage_result] user_id : {dto.user_id}, ticket_id : {dto.ticket_id}, error : {e}"
            )
            raise NotUniqueErrorException(type_="T200")

    def create_promotion_usage_count(self, dto: UseTicketDto, promotion_id: int):
        try:
            promotion_usage_count = PromotionUsageCountModel(
                promotion_id=promotion_id, user_id=dto.user_id, usage_count=1
            )
            session.add(promotion_usage_count)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[PaymentRepository][create_promotion_usage_count] user_id : {dto.user_id}, promotion_id : {promotion_id}, error : {e}"
            )
            raise NotUniqueErrorException(type_="T300")

    def update_promotion_usage_count(self, dto: UseTicketDto, promotion_id: int):
        try:
            filters = list()
            filters.append(PromotionUsageCountModel.promotion_id == promotion_id)
            filters.append(PromotionUsageCountModel.user_id == dto.user_id)

            session.query(PromotionUsageCountModel).filter(*filters).update(
                {"usage_count": PromotionUsageCountModel.usage_count + 1}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[PaymentRepository][update_promotion_usage_count] user_id : {dto.user_id}, promotion_id : {promotion_id}, error : {e}"
            )
            raise NotUniqueErrorException(type_="T400")

    def create_ticket_target(self, dto: UseTicketDto, ticket_id: int) -> None:
        try:
            ticket = TicketTargetModel(
                ticket_id=ticket_id, public_house_id=dto.house_id,
            )

            session.add(ticket)
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[PaymentRepository][create_ticket_target] user_id : {dto.user_id}, error : {e}"
            )
            raise NotUniqueErrorException(type_="T500")

    def create_recommend_code(self, user_id: int) -> RecommendCodeEntity:
        try:
            code: str = self._make_recommend_code()
            code_group = int(user_id / 1000)

            recommend_code = RecommendCodeModel(
                user_id=user_id,
                code_group=code_group,
                code=code.lower(),
                code_count=0,
                is_used=False,
            )
            session.add(recommend_code)
            session.commit()

            return recommend_code.to_entity()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[PaymentRepository][create_recommend_code] user_id : {user_id}, error : {e}"
            )
            raise NotUniqueErrorException(type_="T009")

    def _make_recommend_code(self):
        return StringGenerator("[\l]{6}").render_list(1, unique=True)[0]

    def get_recommend_code_by_user_id(
        self, user_id: int
    ) -> Optional[RecommendCodeEntity]:
        recommend_code = (
            session.query(RecommendCodeModel).filter_by(user_id=user_id).first()
        )
        if not recommend_code:
            return None

        return recommend_code.to_entity()

    def get_recommend_code_by_code(
        self, code: str, code_group: int
    ) -> Optional[RecommendCodeEntity]:
        recommend_code = (
            session.query(RecommendCodeModel)
            .filter_by(code=code, code_group=code_group)
            .first()
        )
        if not recommend_code:
            return None

        return recommend_code.to_entity()

    def update_recommend_code_count(self, recommend_code: RecommendCodeEntity):
        try:
            filters = list()
            filters.append(RecommendCodeModel.id == recommend_code.id)

            session.query(RecommendCodeModel).filter(*filters).update(
                {"code_count": RecommendCodeModel.code_count + 1}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[PaymentRepository][update_recommend_code_count] user_id : {recommend_code.user_id}, error : {e}"
            )
            raise Exception

    def update_recommend_code_is_used(self, recommend_code: RecommendCodeEntity):
        try:
            filters = list()
            filters.append(RecommendCodeModel.id == recommend_code.id)

            session.query(RecommendCodeModel).filter(*filters).update({"is_used": True})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[PaymentRepository][update_recommend_code_is_used] user_id : {recommend_code.user_id}, error : {e}"
            )
            raise Exception
