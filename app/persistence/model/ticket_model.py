from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    ForeignKey,
    DateTime,
    SmallInteger,
    Boolean,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import UserModel
from core.domains.user.entity.user_entity import TicketEntity


class TicketModel(db.Model):
    __tablename__ = "tickets"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False)
    type = Column(SmallInteger, nullable=False)
    amount = Column(SmallInteger, nullable=False)
    sign = Column(String(5), nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_by = Column(String(6), nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_server_timestamp(), nullable=False)

    ticket_targets = relationship(
        "TicketTargetModel", backref=backref("tickets"), uselist=True
    )

    def to_entity(self) -> TicketEntity:
        return TicketEntity(
            id=self.id,
            user_id=self.user_id,
            type=self.type,
            amount=self.amount,
            sign=self.sign,
            is_active=self.is_active,
            created_by=self.created_by,
            created_at=self.created_at,
            ticket_targets=[
                ticket_target.to_entity() for ticket_target in self.ticket_targets
            ]
            if self.ticket_targets
            else None,
        )
