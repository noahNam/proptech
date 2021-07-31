from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    SmallInteger,
    Boolean,
    String,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.entity.house_entity import PromotionEntity


class PromotionModel(db.Model):
    __tablename__ = "promotions"

    id = Column(
        SmallInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    type = Column(String(4), nullable=False)
    max_count = Column(SmallInteger, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    promotion_houses = relationship(
        "PromotionHouseModel", backref=backref("promotions"), uselist=True
    )
    promotion_usage_count = relationship(
        "PromotionUsageCountModel", backref=backref("promotions"), uselist=False
    )

    def to_entity(self) -> PromotionEntity:
        return PromotionEntity(
            id=self.id,
            max_count=self.user_id,
            is_active=self.type,
            created_at=self.amount,
            updated_at=self.sign,
            promotion_houses=[
                promotion_house.to_entity() for promotion_house in self.promotion_houses
            ]
            if self.promotion_houses
            else None,
            promotion_usage_count=self.promotion_usage_count.to_entity()
            if self.promotion_usage_count
            else None,
        )
