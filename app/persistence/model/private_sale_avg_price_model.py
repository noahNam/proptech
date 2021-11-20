from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    String,
    Float,
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
    pyoung = Column(Float, nullable=False)
    default_trade_pyoung = Column(Float, nullable=True)
    default_deposit_pyoung = Column(Float, nullable=True)
    pyoung_div = Column(String(1), nullable=False)
    trade_price = Column(Integer, nullable=True)
    deposit_price = Column(Integer, nullable=True)
    max_trade_contract_date = Column(String(8), nullable=True)
    max_deposit_contract_date = Column(String(8), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> PrivateSaleAvgPriceEntity:
        return PrivateSaleAvgPriceEntity(
            trade_info=PrivateSaleAvgPriceTradeEntity(
                pyoung=self.pyoung,
                trade_price=self.trade_price,
                max_trade_contract_date=self.max_trade_contract_date,
                default_trade_pyoung=self.default_trade_pyoung,
            ),
            deposit_info=PrivateSaleAvgPriceDepositEntity(
                pyoung=self.pyoung,
                deposit_price=self.deposit_price,
                max_deposit_contract_date=self.max_deposit_contract_date,
                default_deposit_pyoung=self.default_deposit_pyoung,
            ),
        )
