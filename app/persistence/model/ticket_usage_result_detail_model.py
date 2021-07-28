from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    SmallInteger,
)

from app import db
from core.domains.user.entity.user_entity import TicketUsageResultDetailEntity


class TicketUsageResultDetailModel(db.Model):
    __tablename__ = "ticket_usage_result_details"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    ticket_usage_result_id = Column(BigInteger, nullable=False, index=True)
    house_structure_type = Column(String(5), nullable=False)
    subscription_type = Column(String(10), nullable=False)
    rank = Column(SmallInteger, nullable=False)

    def to_entity(self) -> TicketUsageResultDetailEntity:
        return TicketUsageResultDetailEntity(
            id=self.id,
            ticket_usage_result_id=self.ticket_usage_result_id,
            house_type=self.house_type,
            subscription_type=self.subscription_type,
            rank=self.rank,
        )
