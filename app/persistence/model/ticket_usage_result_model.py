from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    Boolean,
    String,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.report.entity.report_entity import TicketUsageResultEntity


class TicketUsageResultModel(db.Model):
    __tablename__ = "ticket_usage_results"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, nullable=False, index=True)
    type = Column(String(5), nullable=False)
    public_house_id = Column(BigInteger, nullable=True)
    ticket_id = Column(BigInteger, nullable=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    house_type_ranks = relationship(
        "HouseTypeRankModel",
        backref=backref("ticket_usage_results"),
        uselist=True,
        primaryjoin="foreign(TicketUsageResultModel.id)== HouseTypeRankModel.ticket_usage_result_id",
    )

    user_analysis = relationship(
        "UserAnalysisModel",
        backref=backref("ticket_usage_results"),
        uselist=True,
        primaryjoin="foreign(TicketUsageResultModel.id)== UserAnalysisModel.ticket_usage_result_id",
    )

    predicted_competitions = relationship(
        "PredictedCompetitionModel",
        backref=backref("ticket_usage_results"),
        uselist=True,
        primaryjoin="foreign(TicketUsageResultModel.id)== PredictedCompetitionModel.ticket_usage_result_id",
    )

    def to_entity(self) -> TicketUsageResultEntity:
        return TicketUsageResultEntity(
            id=self.id,
            user_id=self.user_id,
            type=self.type,
            public_house_id=self.public_house_id,
            ticket_id=self.ticket_id,
            is_active=self.is_active,
            created_at=self.created_at,
            tickets=[
                house_type_rank.to_entity() for house_type_rank in self.house_type_ranks
            ]
            if self.house_type_ranks
            else [],
            user_analysis=[analysis.to_entity() for analysis in self.user_analysis]
            if self.user_analysis
            else [],
            predicted_competitions=[
                predicted_competition.to_entity()
                for predicted_competition in self.predicted_competitions
            ]
            if self.predicted_competitions
            else [],
        )
