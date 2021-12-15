from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Boolean,
    DateTime,
    SmallInteger,
    UniqueConstraint,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app import db
from app.persistence.model import UserModel
from core.domains.house.entity.house_entity import InterestHouseEntity


class InterestHouseModel(db.Model):
    __tablename__ = "interest_houses"
    __table_args__ = (UniqueConstraint("user_id", "house_id", "type"),)

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False, index=True,)
    house_id = Column(BigInteger, nullable=False, index=True)
    type = Column(SmallInteger, nullable=False)
    is_like = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    users = relationship("UserModel", back_populates="interest_houses")

    def to_entity(self) -> InterestHouseEntity:
        return InterestHouseEntity(
            id=self.id,
            user_id=self.user_id,
            house_id=self.house_id,
            type=self.type,
            is_like=self.is_like,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
