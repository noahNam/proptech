from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    SmallInteger,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.entity.house_entity import PublicSaleAvgPriceEntity


class PublicSaleAvgPriceModel(db.Model):
    __tablename__ = "public_sale_avg_prices"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    public_sales_id = Column(BigInteger, nullable=False, index=True)
    pyoung = Column(SmallInteger, nullable=False)
    default_pyoung = Column(SmallInteger, nullable=False)
    supply_price = Column(Integer, nullable=True)
    avg_competition = Column(SmallInteger, nullable=True)
    min_score = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> PublicSaleAvgPriceEntity:
        return PublicSaleAvgPriceEntity(
            pyoung=self.pyoung, supply_price=self.supply_price, avg_competition=self.avg_competition, min_score=self.min_score
        )
