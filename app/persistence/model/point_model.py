from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    ForeignKey,
    DateTime, SmallInteger,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import UserModel
from core.domains.user.entity.user_entity import PointEntity


class PointModel(db.Model):
    __tablename__ = "points"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False)
    type = Column(SmallInteger, nullable=False)
    amount = Column(Integer, nullable=False)
    sign = Column(String(5), nullable=False)
    created_by = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    point_type = relationship(
        "PointTypeModel", backref=backref("points"), uselist=False
    )

    def to_entity(self) -> PointEntity:
        return PointEntity(
            id=self.id,
            user_id=self.user_id,
            type=self.type,
            amount=self.amount,
            sign=self.sign,
            created_by=self.created_by,
            created_at=self.created_at,
            point_type=self.point_type.to_entity() if self.point_type else None,
        )
