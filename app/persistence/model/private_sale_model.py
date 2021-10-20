from typing import Optional

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    DateTime,
    Enum,
    String,
    SmallInteger,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.real_estate_model import RealEstateModel
from core.domains.house.entity.house_entity import (
    PrivateSaleEntity,
    PrivateSaleBoundingEntity,
    PrivateSaleAvgPriceTradeEntity,
    PrivateSaleAvgPriceDepositEntity,
    NearHousePrivateSaleEntity,
)
from core.domains.house.enum.house_enum import BuildTypeEnum


class PrivateSaleModel(db.Model):
    __tablename__ = "private_sales"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    real_estate_id = Column(
        BigInteger,
        ForeignKey(RealEstateModel.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    name = Column(String(50), nullable=True)
    building_type = Column(
        Enum(BuildTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    supply_household = Column(SmallInteger, nullable=True)
    move_in_year = Column(String(8), nullable=True)
    construct_company = Column(String(30), nullable=True)
    dong_num = Column(SmallInteger, nullable=True)
    park_space_num = Column(Float, nullable=True)
    heating_type = Column(String(10), nullable=True)
    floor_area_ratio = Column(SmallInteger, nullable=True)
    building_cover_ratio = Column(SmallInteger, nullable=True)
    trade_status = Column(SmallInteger, nullable=False, default=0)
    deposit_status = Column(SmallInteger, nullable=False, default=0)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    is_available = Column(Boolean, nullable=False, default=False)

    private_sale_details = relationship(
        "PrivateSaleDetailModel",
        backref=backref("private_sales", cascade="all, delete"),
    )

    dong_infos = relationship(
        "DongInfoModel", backref=backref("private_sales", cascade="all, delete"),
    )

    private_sale_avg_prices = relationship(
        "PrivateSaleAvgPriceModel",
        backref=backref("private_sale_avg_prices"),
        uselist=True,
        primaryjoin="foreign(PrivateSaleModel.id)== PrivateSaleAvgPriceModel.private_sales_id",
        viewonly=True,
    )

    # 1:M relationship
    private_sale_photos = relationship(
        "PrivateSalePhotoModel", backref=backref("private_sales"), uselist=True
    )

    def to_entity(self) -> PrivateSaleEntity:
        return PrivateSaleEntity(
            id=self.id,
            real_estate_id=self.real_estate_id,
            building_type=self.building_type,
            private_sale_details=[
                private_sale_details.to_entity()
                for private_sale_details in self.private_sale_details
            ]
            if self.private_sale_details
            else None,
            trade_status=self.trade_status,
            deposit_status=self.deposit_status,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def to_bounding_entity(self) -> PrivateSaleBoundingEntity:
        return PrivateSaleBoundingEntity(
            id=self.id,
            building_type=self.building_type,
            default_pyoung=self.default_pyoung,
            trade_info=[
                PrivateSaleAvgPriceTradeEntity(
                    pyoung=private_sale_avg_price.pyoung,
                    trade_price=private_sale_avg_price.trade_price,
                    trade_visible=private_sale_avg_price.trade_visible,
                )
                for private_sale_avg_price in self.private_sale_avg_prices
            ]
            if self.private_sale_avg_prices
            else None,
            deposit_info=[
                PrivateSaleAvgPriceDepositEntity(
                    pyoung=private_sale_avg_price.pyoung,
                    deposit_price=private_sale_avg_price.deposit_price,
                    deposit_visible=private_sale_avg_price.deposit_visible,
                )
                for private_sale_avg_price in self.private_sale_avg_prices
            ]
            if self.private_sale_avg_prices
            else None,
            trade_status=self.trade_status,
            deposit_status=self.deposit_status,
        )

    @property
    def default_pyoung(self) -> Optional[int]:
        return (
            self.private_sale_avg_prices[0].default_pyoung
            if self.private_sale_avg_prices
            else None
        )

    def to_near_house_entity(self) -> NearHousePrivateSaleEntity:
        return NearHousePrivateSaleEntity(
            id=self.id,
            building_type=self.building_type,
            default_pyoung=self.default_pyoung,
            trade_info=[
                PrivateSaleAvgPriceTradeEntity(
                    pyoung=private_sale_avg_price.pyoung,
                    trade_price=private_sale_avg_price.trade_price,
                    trade_visible=private_sale_avg_price.trade_visible,
                )
                for private_sale_avg_price in self.private_sale_avg_prices
            ]
            if self.private_sale_avg_prices
            else None,
            trade_status=self.trade_status,
        )
