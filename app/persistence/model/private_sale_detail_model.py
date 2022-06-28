from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    Boolean,
    String,
    func,
    Numeric,
    SmallInteger,
)

from app import db
from core.domains.house.entity.house_entity import PrivateSaleDetailEntity


class PrivateSaleDetailModel(db.Model):
    __tablename__ = "private_sale_details"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    private_sale_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )
    private_area = Column(Numeric(6, 2), nullable=True)
    supply_area = Column(Numeric(6, 2), nullable=True)
    contract_date = Column(String(8), nullable=True)
    contract_ym = Column(SmallInteger, nullable=True, index=True)
    deposit_price = Column(Integer, nullable=True)
    rent_price = Column(Integer, nullable=True)
    trade_price = Column(Integer, nullable=True)
    floor = Column(SmallInteger, nullable=True)
    trade_type = Column(String(5), nullable=False, index=True,)
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> PrivateSaleDetailEntity:
        return PrivateSaleDetailEntity(
            id=self.id,
            private_sale_id=self.private_sale_id,
            private_area=self.private_area,
            supply_area=self.supply_area,
            contract_date=self.contract_date,
            contract_ym=self.contract_ym,
            deposit_price=self.deposit_price,
            rent_price=self.rent_price,
            trade_price=self.trade_price,
            floor=self.floor,
            trade_type=self.trade_type,
            is_available=self.is_available,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
