from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    SmallInteger,
    ForeignKey,
    func,
    Boolean,
)
from sqlalchemy.orm import relationship

from app import db
from app.persistence.model import UserModel
from core.domains.user.entity.user_entity import RecentlyViewEntity


class RecentlyViewModel(db.Model):
    __tablename__ = "recently_views"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False, index=True)
    house_id = Column(BigInteger, nullable=False, index=True)
    type = Column(SmallInteger, nullable=False)
    is_available = Column(Boolean, nullable=True, default=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=True
    )

    users = relationship("UserModel", back_populates="recently_views")

    def to_entity(self) -> RecentlyViewEntity:
        return RecentlyViewEntity(
            id=self.id,
            user_id=self.user_id,
            house_id=self.house_id,
            type=self.type,
            is_available=self.is_available,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
