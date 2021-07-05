from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
    String,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.real_estate_model import RealEstateModel
from core.domains.map.entity.map_entity import PreSaleEntity
from core.domains.map.enum.map_enum import HousingCategoryEnum, RentTypeEnum, PreSaleTypeEnum


class PreSaleModel(db.Model):
    __tablename__ = "pre_sales"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    real_estate_id = Column(BigInteger,
                            ForeignKey(RealEstateModel.id, ondelete="CASCADE"),
                            nullable=False)
    name = Column(String(50), nullable=False)
    region = Column(String(20), nullable=False)
    housing_category = Column(Enum(HousingCategoryEnum, values_callable=lambda obj: [e.value for e in obj]),
                              nullable=False)
    rent_type = Column(Enum(RentTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
                       nullable=False)
    trade_type = Column(Enum(PreSaleTypeEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    construct_company = Column(String(30), nullable=True)
    private_area = Column(Float, nullable=False)
    supply_area = Column(Float, nullable=False)
    supply_price = Column(Integer, nullable=False)
    supply_household = Column(Integer, nullable=False)
    notes = Column(String(50), nullable=True)
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    # 1:1 relationship
    real_trades = relationship("SubscriptionScheduleModel",
                               backref=backref("pre_sales"),
                               uselist=False)

    def __repr__(self):
        return (
            f"PreSale({self.id}, "
            f"{self.real_estate_id}, "
            f"{self.name}, "
            f"{self.region}, "
            f"{self.housing_category}, "
            f"{self.rent_type}, "
            f"{self.trade_type}, "
            f"{self.construct_company}, "
            f"{self.housing_type}, "
            f"{self.supply_price}, "
            f"{self.supply_area}, "
            f"{self.notes}, "
            f"{self.is_available}, "
            f"{self.created_at}, "
            f"{self.updated_at})"
        )

    def to_entity(self) -> PreSaleEntity:
        return PreSaleEntity(
            id=self.id,
            real_estate_id=self.real_estate_id,
            name=self.name,
            region=self.region,
            housing_category=self.housing_category,
            rent_type=self.rent_type,
            trade_type=self.trade_price,
            construct_company=self.construct_company,
            housing_type=self.housing_type,
            supply_price=self.supply_price,
            supply_area=self.supply_area,
            notes=self.notes,
            is_available=self.is_available,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
