from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship, backref, column_property

from app import db
from core.domains.house.entity.house_entity import RealEstateEntity, BoundingRealEstateEntity


class RealEstateModel(db.Model):
    __tablename__ = "real_estates"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
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
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326).with_variant(String, "sqlite"), nullable=True)

    latitude = column_property(coordinates.ST_X())
    longitude = column_property(coordinates.ST_Y())

    private_sales = relationship("PrivateSaleModel", backref=backref("real_estates", cascade="all, delete"))
    public_sales = relationship("PublicSaleModel", backref=backref("real_estates", cascade="all, delete"),
                                uselist=False)

    def __repr__(self):
        return (
            f"RealEstate({self.id}, "
            f"{self.name}, "
            f"{self.road_address}, "
            f"{self.jibun_address}, "
            f"{self.si_do}, "
            f"{self.si_gun_gu}, "
            f"{self.dong_myun}, "
            f"{self.ri}, "
            f"{self.road_name}, "
            f"{self.road_number}, "
            f"{self.land_number}, "
            f"{self.is_available}, "
            f"{self.coordinates})"
        )

    def to_entity(self, lat, lon) -> RealEstateEntity:
        return RealEstateEntity(
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
            # 쿼리로부터 좌표 얻기
            latitude=lat,
            longitude=lon
        )

    def to_bounding_entity(self) -> BoundingRealEstateEntity:
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
            private_sales=[private_sale.to_entity() for private_sale in
                           self.private_sales] if self.private_sales else None,
            public_sales=self.public_sales.to_entity() if self.public_sales else None
        )
