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
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.real_estate_model import RealEstateModel
from core.domains.map.entity.real_trade_entity import RealTradeEntity
from core.domains.map.enum.map_enum import BuildTypeEnum, RealTradeTypeEnum


class RealTradeModel(db.Model):
    __tablename__ = "real_trades"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    real_estate_id = Column(BigInteger, ForeignKey(RealEstateModel.id), nullable=False)
    area = Column(Float, nullable=False)
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

    def __repr__(self):
        return (
            f"RealTrade({self.id}, "
            f"{self.real_estate_id}, "
            f"{self.area}, "
            f"{self.supply_area}, "
            f"{self.contract_date}, "
            f"{self.deposit_price}, "
            f"{self.rent_price}, "
            f"{self.trade_price}, "
            f"{self.floor}, "
            f"{self.trade_type}, "
            f"{self.building_type}, "
            f"{self.is_available}, "
            f"{self.created_at}, "
            f"{self.updated_at})"
        )

    def to_entity(self) -> RealTradeEntity:
        return RealTradeEntity(
            id=self.id,
            real_estate_id=self.real_estate_id,
            area=self.area,
            supply_area=self.supply_area,
            contract_date=self.contract_date,
            deposit_price=self.deposit_price,
            rent_price=self.rent_price,
            trade_price=self.trade_price,
            floor=self.floor,
            trade_type=self.trade_type,
            building_type=self.building_type,
            is_available=self.is_available,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
