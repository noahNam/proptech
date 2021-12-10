from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    SmallInteger,
    Boolean,
    Enum,
    String, func,
)

from app import db
from app.persistence.model.private_sale_model import PrivateSaleModel
from core.domains.house.entity.house_entity import PrivateSaleDetailEntity
from core.domains.house.enum.house_enum import RealTradeTypeEnum


class PrivateSaleDetailModel(db.Model):
    __tablename__ = "private_sale_details"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    private_sales_id = Column(
        BigInteger, ForeignKey(PrivateSaleModel.id), nullable=False, index=True,
    )
    private_area = Column(Float, nullable=False)
    supply_area = Column(Float, nullable=False)
    contract_date = Column(String(8), nullable=True)
    contract_ym = Column(Integer, nullable=True, index=True)
    deposit_price = Column(Integer, nullable=False)
    rent_price = Column(Integer, nullable=False)
    trade_price = Column(Integer, nullable=False)
    floor = Column(SmallInteger, nullable=False)
    trade_type = Column(
        Enum(RealTradeTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> PrivateSaleDetailEntity:
        return PrivateSaleDetailEntity(
            id=self.id,
            private_sales_id=self.private_sales_id,
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
