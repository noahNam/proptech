from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, backref, column_property

from app import db
from core.domains.house.entity.house_entity import (
    BoundingRealEstateEntity,
    RealEstateWithPrivateSaleEntity,
    HousePublicDetailEntity,
    CalenderInfoEntity,
)


class RealEstateModel(db.Model):
    __tablename__ = "real_estates"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    name = Column(String(50), nullable=True)
    road_address = Column(String(100), nullable=False)
    jibun_address = Column(String(100), nullable=False)
    si_do = Column(String(20), nullable=False)
    si_gun_gu = Column(String(16), nullable=False)
    dong_myun = Column(String(16), nullable=False)
    ri = Column(String(12), nullable=True)
    road_name = Column(String(30), nullable=True)
    road_number = Column(String(10), nullable=True)
    land_number = Column(String(10), nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    coordinates = Column(
        Geometry(geometry_type="POINT", srid=4326).with_variant(String, "sqlite"),
        nullable=True,
    )

    jibun_address_ts = Column(
        TSVECTOR().with_variant(String(100), "sqlite"), nullable=True
    )
    road_address_ts = Column(
        TSVECTOR().with_variant(String(100), "sqlite"), nullable=True
    )

    latitude = column_property(coordinates.ST_Y())
    longitude = column_property(coordinates.ST_X())

    private_sales = relationship(
        "PrivateSaleModel",
        backref=backref("real_estates", cascade="all, delete"),
        uselist=False,
    )
    public_sales = relationship(
        "PublicSaleModel",
        backref=backref("real_estates", cascade="all, delete"),
        uselist=False,
    )

    def to_bounding_entity(
        self,
        avg_trade: Optional[float],
        avg_deposit: Optional[float],
        avg_rent: Optional[float],
        avg_supply: Optional[float],
        avg_private_pyoung: Optional[float],
        avg_public_pyoung: Optional[float],
    ) -> BoundingRealEstateEntity:
        return BoundingRealEstateEntity(
            id=self.id,
            name=self.name,
            road_address=self.road_address,
            jibun_address=self.jibun_address,
            si_do=self.si_do,
            si_gun_gu=self.si_gun_gu,
            dong_myun=self.dong_myun,
            ri=self.ri,
            road_name=self.road_name,
            road_number=self.road_number,
            land_number=self.land_number,
            is_available=self.is_available,
            latitude=self.latitude,
            longitude=self.longitude,
            avg_trade_price=avg_trade,
            avg_deposit_price=avg_deposit,
            avg_rent_price=avg_rent,
            avg_supply_price=avg_supply,
            avg_private_pyoung_number=avg_private_pyoung,
            avg_public_pyoung_number=avg_public_pyoung,
            private_sales=self.private_sales.to_entity()
            if self.private_sales
            else None,
            public_sales=self.public_sales.to_entity() if self.public_sales else None,
        )

    def to_estate_with_private_sales_entity(
        self, avg_trade: Optional[float], avg_private_pyoung: Optional[float]
    ) -> RealEstateWithPrivateSaleEntity:
        return RealEstateWithPrivateSaleEntity(
            id=self.id,
            name=self.name,
            road_address=self.road_address,
            jibun_address=self.jibun_address,
            si_do=self.si_do,
            si_gun_gu=self.si_gun_gu,
            dong_myun=self.dong_myun,
            ri=self.ri,
            road_name=self.road_name,
            road_number=self.road_number,
            land_number=self.land_number,
            is_available=self.is_available,
            latitude=self.latitude,
            longitude=self.longitude,
            avg_trade_price=avg_trade,
            avg_private_pyoung_number=avg_private_pyoung,
            private_sales=self.private_sales.to_entity()
            if self.private_sales
            else None,
        )

    def to_house_with_public_detail_entity(
        self,
        is_like: bool,
        min_pyoung_number: Optional[float],
        max_pyoung_number: Optional[float],
        min_supply_area: Optional[float],
        max_supply_area: Optional[float],
        avg_supply_price: Optional[float],
        supply_price_per_pyoung: Optional[float],
        min_acquisition_tax: int,
        max_acquisition_tax: int,
        near_houses: Optional[list],
    ) -> HousePublicDetailEntity:
        return HousePublicDetailEntity(
            id=self.id,
            name=self.name,
            road_address=self.road_address,
            jibun_address=self.jibun_address,
            si_do=self.si_do,
            si_gun_gu=self.si_gun_gu,
            dong_myun=self.dong_myun,
            ri=self.ri,
            road_name=self.road_name,
            road_number=self.road_number,
            land_number=self.land_number,
            is_available=self.is_available,
            latitude=self.latitude,
            longitude=self.longitude,
            is_like=is_like,
            min_pyoung_number=min_pyoung_number,
            max_pyoung_number=max_pyoung_number,
            min_supply_area=min_supply_area,
            max_supply_area=max_supply_area,
            avg_supply_price=avg_supply_price,
            supply_price_per_pyoung=supply_price_per_pyoung,
            min_acquisition_tax=min_acquisition_tax,
            max_acquisition_tax=max_acquisition_tax,
            public_sales=self.public_sales.to_entity() if self.public_sales else None,
            near_houses=near_houses,
        )

    def to_calender_info_entity(self, is_like: bool) -> CalenderInfoEntity:
        return CalenderInfoEntity(
            is_like=is_like,
            id=self.id,
            name=self.name,
            road_address=self.road_address,
            jibun_address=self.jibun_address,
            public_sale=self.public_sales.to_calender_entity()
            if self.public_sales
            else None,
        )
