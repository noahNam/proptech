from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    SmallInteger,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.entity.house_entity import (
    PrivateSaleAvgPriceEntity,
    PrivateSaleAvgPriceTradeEntity,
    PrivateSaleAvgPriceDepositEntity,
)


class PrivateSaleAvgPriceModel(db.Model):
    __tablename__ = "private_sale_avg_prices"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    private_sales_id = Column(BigInteger, nullable=False, index=True)
    pyoung = Column(SmallInteger, nullable=False)
    default_pyoung = Column(SmallInteger, nullable=False)
    trade_price = Column(Integer, nullable=True)
    deposit_price = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> PrivateSaleAvgPriceEntity:
        return PrivateSaleAvgPriceEntity(
            trade_info=PrivateSaleAvgPriceTradeEntity(
                pyoung=self.pyoung, trade_price=self.trade_price
            ),
            deposit_info=PrivateSaleAvgPriceDepositEntity(
                pyoung=self.pyoung, deposit_price=self.deposit_price
            ),
        )
