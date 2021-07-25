from sqlalchemy import (
    Column,
    Integer,
    String,
    SmallInteger,
)

from app import db
from core.domains.user.entity.user_entity import PointTypeEntity


class PointTypeModel(db.Model):
    __tablename__ = "point_types"

    id = Column(
        SmallInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    name = Column(String(20), nullable=False)
    division = Column(String(7), nullable=False)

    def to_entity(self) -> PointTypeEntity:
        return PointTypeEntity(id=self.id, name=self.name, division=self.division,)
