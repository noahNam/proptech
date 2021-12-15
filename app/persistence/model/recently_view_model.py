from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    SmallInteger,
    ForeignKey,
    func,
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
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False, index=True,)
    house_id = Column(BigInteger, nullable=False)
    type = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)

    users = relationship("UserModel", back_populates="recently_views")

    def to_entity(self) -> RecentlyViewEntity:
        return RecentlyViewEntity(
            id=self.id,
            user_id=self.user_id,
            house_id=self.house_id,
            type=self.type,
            created_at=self.created_at,
        )
