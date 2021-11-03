from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    SmallInteger,
)

from app import db
from app.persistence.model.promotion_model import PromotionModel
from core.domains.payment.entity.payment_entity import PromotionHouseEntity


class PromotionHouseModel(db.Model):
    __tablename__ = "promotion_houses"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    promotion_id = Column(
        SmallInteger, ForeignKey(PromotionModel.id), nullable=False, index=True,
    )
    house_id = Column(BigInteger, nullable=False, index=True)

    def to_entity(self) -> PromotionHouseEntity:
        return PromotionHouseEntity(
            id=self.id, promotion_id=self.promotion_id, house_id=self.house_id,
        )
