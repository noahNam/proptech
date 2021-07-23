from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
)

from app import db
from core.domains.user.entity.user_entity import PointTypeEntity


class PointTypeModel(db.Model):
    __tablename__ = "point_types"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    name = Column(String(20), nullable=False)
    division = Column(String(7), nullable=False)

    def to_entity(self) -> PointTypeEntity:
        return PointTypeEntity(
            id=self.id,
            name=self.name,
            division=self.division,
        )
