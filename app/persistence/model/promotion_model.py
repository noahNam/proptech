from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    SmallInteger,
    Boolean,
    String, func,
)
from sqlalchemy.orm import relationship, backref

from app import db
from core.domains.payment.entity.payment_entity import PromotionEntity


class PromotionModel(db.Model):
    __tablename__ = "promotions"

    id = Column(
        SmallInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    type = Column(String(4), nullable=False)
    div = Column(String(5), nullable=False)
    max_count = Column(SmallInteger, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    promotion_houses = relationship(
        "PromotionHouseModel", backref=backref("promotions"), uselist=True
    )
    promotion_usage_count = relationship(
        "PromotionUsageCountModel", backref=backref("promotions"), uselist=False
    )

    def to_entity(self) -> PromotionEntity:
        return PromotionEntity(
            id=self.id,
            type=self.type,
            div=self.div,
            max_count=self.max_count,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
            promotion_houses=[
                promotion_house.to_entity() for promotion_house in self.promotion_houses
            ]
            if self.promotion_houses
            else None,
            promotion_usage_count=self.promotion_usage_count.to_entity()
            if self.promotion_usage_count
            else None,
        )
