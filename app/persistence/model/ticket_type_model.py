from sqlalchemy import (
    Column,
    String,
    SmallInteger, Integer,
)

from app import db
from core.domains.user.entity.user_entity import TicketTypeEntity


class TicketTypeModel(db.Model):
    __tablename__ = "ticket_types"

    id = Column(
        SmallInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    division = Column(String(10), nullable=False)

    def to_entity(self) -> TicketTypeEntity:
        return TicketTypeEntity(id=self.id, division=self.division,)
