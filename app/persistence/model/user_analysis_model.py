from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    SmallInteger,
    DateTime,
    String,
    func,
)

from app import db
from core.domains.report.entity.report_entity import UserAnalysisEntity


class UserAnalysisModel(db.Model):
    __tablename__ = "user_analysis"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    ticket_usage_result_id = Column(BigInteger, nullable=False, index=True)
    div = Column(String(1), nullable=False)
    category = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)

    def to_entity(self) -> UserAnalysisEntity:
        return UserAnalysisEntity(
            id=self.id,
            ticket_usage_result_id=self.ticket_usage_result_id,
            div=self.div,
            category=self.category,
            created_at=self.created_at,
        )
