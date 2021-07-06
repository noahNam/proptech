from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Boolean,
    DateTime, SmallInteger, UniqueConstraint,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.entity.house_entity import InterestHouseEntity


class InterestHouseModel(db.Model):
    __tablename__ = "interest_houses"
    __table_args__ = (
        UniqueConstraint('user_id', 'ref_id', 'type'),
    )

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, nullable=False, index=True)
    ref_id = Column(BigInteger, nullable=False, index=True)
    type = Column(SmallInteger, nullable=False)
    is_like = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> InterestHouseEntity:
        return InterestHouseEntity(
            id=self.id,
            user_id=self.user_id,
            ref_id=self.ref_id,
            is_like=self.is_like,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
