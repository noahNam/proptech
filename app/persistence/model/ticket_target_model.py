from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
)

from app import db
from app.persistence.model import TicketModel
from core.domains.payment.entity.payment_entity import TicketTargetEntity


class TicketTargetModel(db.Model):
    __tablename__ = "ticket_targets"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    ticket_id = Column(BigInteger, ForeignKey(TicketModel.id), nullable=False, index=True,)
    public_house_id = Column(BigInteger, nullable=False)

    def to_entity(self) -> TicketTargetEntity:
        return TicketTargetEntity(
            id=self.id, ticket_id=self.ticket_id, public_house_id=self.public_house_id,
        )
