from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Numeric, DateTime, func,
)

from app import db
from core.domains.house.entity.house_entity import TypeInfoEntity


class TypeInfoModel(db.Model):
    __tablename__ = "type_infos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    dong_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )
    private_area = Column(Numeric(6,2), nullable=True)
    supply_area = Column(Numeric(6,2), nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> TypeInfoEntity:
        return TypeInfoEntity(
            id=self.id,
            dong_id=self.dong_id,
            private_area=self.private_area,
            supply_area=self.supply_area,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )