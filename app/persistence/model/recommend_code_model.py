from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    SmallInteger, Boolean,
)
from app import db
from core.domains.payment.entity.payment_entity import RecommendCodeEntity


class RecommendCodeModel(db.Model):
    __tablename__ = "recommend_codes"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, nullable=False, index=True)
    code = Column(String(4), nullable=False)
    code_count = Column(SmallInteger, nullable=False, default=0)
    is_used = Column(Boolean, nullable=False, default=0)

    def to_entity(self) -> RecommendCodeEntity:
        return RecommendCodeEntity(
            id=self.id,
            user_id=self.user_id,
            code=self.code,
            code_count=self.last_update_code,
            is_used=self.is_used,
        )
