from typing import List, Optional

from sqlalchemy import exists
from sqlalchemy.orm import selectinload

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.persistence.model import TicketUsageResultModel, SurveyResultModel
from core.domains.payment.enum.payment_enum import TicketUsageTypeEnum
from core.domains.report.entity.report_entity import PredictedCompetitionEntity, SurveyResultEntity
from core.exceptions import NotUniqueErrorException

logger = logger_.getLogger(__name__)


class ReportRepository:
    def get_ticket_usage_results(self, user_id: int) -> List[int]:
        query = session.query(TicketUsageResultModel).filter_by(
            user_id=user_id, is_active=True
        )
        query_set = query.all()

        if not query_set:
            return []
        return [query.public_house_id for query in query_set]

    def is_ticket_usage_for_house(self, user_id: int, house_id: int) -> bool:
        return session.query(
            exists()
                .where(TicketUsageResultModel.public_house_id == house_id)
                .where(TicketUsageResultModel.user_id == user_id)
                .where(TicketUsageResultModel.type == TicketUsageTypeEnum.HOUSE.value)
        ).scalar()

    def is_ticket_usage_for_user(self, user_id: int, ) -> bool:
        return session.query(
            exists()
                .where(TicketUsageResultModel.user_id == user_id)
                .where(TicketUsageResultModel.type == TicketUsageTypeEnum.USER.value)
        ).scalar()

    def update_ticket_usage_result(
            self, user_id: int, public_house_id: Optional[int], ticket_id: int
    ) -> None:
        try:
            filters = list()
            filters.append(TicketUsageResultModel.user_id == user_id)
            if public_house_id:
                filters.append(
                    TicketUsageResultModel.public_house_id == public_house_id
                )
                filters.append(
                    TicketUsageResultModel.type == TicketUsageTypeEnum.HOUSE.value
                )
            else:
                filters.append(
                    TicketUsageResultModel.type == TicketUsageTypeEnum.USER.value
                )

            session.query(TicketUsageResultModel).filter(*filters).update(
                {"ticket_id": ticket_id}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[update_ticket_usage_result][update_ticket_usage_result] user_id : {user_id}, ticket_id : {ticket_id}, error : {e}"
            )
            raise NotUniqueErrorException(type_="T200")

    def get_expected_competition(
            self, user_id: int, house_id: int
    ) -> List[PredictedCompetitionEntity]:
        filters = list()
        filters.append(TicketUsageResultModel.user_id == user_id)
        filters.append(TicketUsageResultModel.type == TicketUsageTypeEnum.HOUSE.value)
        filters.append(TicketUsageResultModel.public_house_id == house_id)
        filters.append(TicketUsageResultModel.is_active == True)

        query = (
            session.query(TicketUsageResultModel)
                .join(TicketUsageResultModel.predicted_competitions)
                .options(selectinload(TicketUsageResultModel.predicted_competitions))
                .filter(*filters)
        )

        query_set = query.first()

        if not query_set:
            return []

        return query_set.to_entity().predicted_competitions

    def get_user_survey_results(
            self, user_id: int,
    ) -> Optional[SurveyResultEntity]:
        query = (
            session.query(SurveyResultModel)
                .filter_by(user_id=user_id)
        )
        query_set = query.first()

        if not query_set:
            return None

        return query_set.to_entity()
