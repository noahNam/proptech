from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.user.entity.user_entity import TicketUsageResultEntity


class TicketUsageResultModel(db.Model):
    __tablename__ = "ticket_usage_results"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, nullable=False, index=True)
    public_house_id = Column(BigInteger, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    ticket_usage_result_details = relationship(
        "TicketUsageResultDetailModel", backref=backref("ticket_usage_results"), uselist=True,
        primaryjoin='foreign(TicketUsageResultModel.id)== TicketUsageResultDetailModel.ticket_usage_result_id'
    )

    def to_entity(self) -> TicketUsageResultEntity:
        return TicketUsageResultEntity(
            id=self.id,
            user_id=self.user_id,
            house_id=self.house_id,
            is_active=self.is_active,
            created_at=self.created_at,
            ticket_usage_result_details=self.ticket_usage_result_details,
        )
