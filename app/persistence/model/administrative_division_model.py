from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    Enum,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.house.entity.house_entity import AdministrativeDivisionEntity
from core.domains.house.enum.house_enum import DivisionLevelEnum


class AdministrativeDivisionModel(db.Model):
    __tablename__ = "administrative_divisions"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )

    name = Column(String(100), nullable=False)
    real_trade_price = Column(Integer, nullable=False)
    real_rent_price = Column(Integer, nullable=False)
    real_deposit_price = Column(Integer, nullable=False)
    public_sale_price = Column(Integer, nullable=False)
    level = Column(Enum(DivisionLevelEnum, values_callable=lambda obj: [e.value for e in obj]),
                   nullable=False)
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326).with_variant(String, "sqlite"), nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def __repr__(self):
        return (
            f"AdministrativeDivision({self.id}', "
            f"{self.name}, "
            f"{self.real_trade_price}, "
            f"{self.real_rent_price}, "
            f"{self.real_deposit_price}, "
            f"{self.public_sale_price}, "
            f"{self.level}, "
            f"{self.coordinates}, "
            f"{self.created_at}, "
            f"{self.updated_at}) "
        )

    def to_entity(self, lat, lon) -> AdministrativeDivisionEntity:
        return AdministrativeDivisionEntity(
            id=self.id,
            name=self.name,
            real_trade_price=self.real_trade_price,
            real_rent_price=self.real_rent_price,
            real_deposit_price=self.real_deposit_price,
            public_sale_price=self.public_sale_price,
            level=self.level,
            # coordinates=self.coordinates,
            latitude=lat,
            longitude=lon,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
