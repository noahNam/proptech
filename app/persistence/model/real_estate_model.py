from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Float,
    Boolean, func,
)
from sqlalchemy.orm import relationship, backref
# from geoalchemy2.shape import to_shape

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
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

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
            # coordinates=make_geometry_point_of_pydantic(lat=lat, lon=lon)
            # todo. 쿼리에서 따로 넣어주는데 해당 entitiy에서 가지고 있어야 하는지?
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
            latitude=func.ST_Y(self.coordinates).label("latitude"),
            longitude=func.ST_X(self.coordinates).label("longitude"),
            private_sales=[private_sale.to_entity() for private_sale in
                           self.private_sales] if self.private_sales else None,
            public_sales=self.public_sales.to_entity() if self.public_sales else None
        )
