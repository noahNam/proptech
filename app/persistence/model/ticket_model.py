from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    ForeignKey,
    DateTime,
    SmallInteger,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import UserModel, TicketTypeModel
from core.domains.user.entity.user_entity import TicketEntity


class TicketModel(db.Model):
    __tablename__ = "tickets"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False)
    type = Column(SmallInteger, ForeignKey(TicketTypeModel.id), nullable=False)
    amount = Column(SmallInteger, nullable=False)
    sign = Column(String(5), nullable=False)
    created_by = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    ticket_type = relationship(
        "TicketTypeModel", backref=backref("tickets"), uselist=False
    )

    def to_entity(self) -> TicketEntity:
        return TicketEntity(
            id=self.id,
            user_id=self.user_id,
            type=self.type,
            amount=self.amount,
            sign=self.sign,
            created_by=self.created_by,
            created_at=self.created_at,
            ticket_type=self.ticket_type.to_entity() if self.ticket_type else None,
        )
