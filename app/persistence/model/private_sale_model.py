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
    Date,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.real_estate_model import RealEstateModel
from core.domains.house.entity.house_entity import PrivateSaleEntity
from core.domains.house.enum.house_enum import BuildTypeEnum, RealTradeTypeEnum


class PrivateSaleModel(db.Model):
    __tablename__ = "private_sales"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    real_estate_id = Column(BigInteger,
                            ForeignKey(RealEstateModel.id, ondelete="CASCADE"),
                            nullable=False)
    private_area = Column(Float, nullable=False)
    supply_area = Column(Float, nullable=False)
    contract_date = Column(DateTime, nullable=False)
    deposit_price = Column(Integer, nullable=False)
    rent_price = Column(Integer, nullable=False)
    trade_price = Column(Integer, nullable=False)
    floor = Column(SmallInteger, nullable=False)
    trade_type = Column(Enum(RealTradeTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
                        nullable=False)
    building_type = Column(Enum(BuildTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
                           nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> PrivateSaleEntity:
        return PrivateSaleEntity(
            id=self.id,
            real_estate_id=self.real_estate_id,
            private_area=self.private_area,
            supply_area=self.supply_area,
            contract_date=self.contract_date,
            deposit_price=self.deposit_price,
            rent_price=self.rent_price,
            trade_price=self.trade_price,
            floor=self.floor,
            trade_type=self.trade_type,
            building_type=self.building_type,
            is_available=self.is_available,
            created_at=self.created_at.date().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.date().strftime("%Y-%m-%d %H:%M:%S")
        )
