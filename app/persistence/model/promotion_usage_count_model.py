from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    SmallInteger,
)

from app import db
from app.persistence.model.promotion_model import PromotionModel
from core.domains.payment.entity.payment_entity import PromotionUsageCountEntity


class PromotionUsageCountModel(db.Model):
    __tablename__ = "promotion_usage_counts"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    promotion_id = Column(SmallInteger, ForeignKey(PromotionModel.id), nullable=False, index=True,)
    user_id = Column(BigInteger, nullable=False, index=True)
    usage_count = Column(SmallInteger, nullable=False, default=0)

    def to_entity(self) -> PromotionUsageCountEntity:
        return PromotionUsageCountEntity(
            id=self.id,
            promotion_id=self.promotion_id,
            user_id=self.user_id,
            usage_count=self.usage_count,
        )
