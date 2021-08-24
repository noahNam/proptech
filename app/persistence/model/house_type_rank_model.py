from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    SmallInteger,
)

from app import db
from core.domains.report.entity.report_entity import HouseTypeRankEntity


class HouseTypeRankModel(db.Model):
    __tablename__ = "house_type_ranks"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    ticket_usage_result_id = Column(BigInteger, nullable=False, index=True)
    house_structure_type = Column(String(5), nullable=False)
    subscription_type = Column(String(10), nullable=False)
    rank = Column(SmallInteger, nullable=False)

    def to_entity(self) -> HouseTypeRankEntity:
        return HouseTypeRankEntity(
            id=self.id,
            ticket_usage_result_id=self.ticket_usage_result_id,
            house_structure_type=self.house_structure_type,
            subscription_type=self.subscription_type,
            rank=self.rank,
        )
