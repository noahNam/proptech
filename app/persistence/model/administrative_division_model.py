from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    Enum,
    Boolean,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import column_property

from app import db
from core.domains.house.entity.house_entity import (
    AdministrativeDivisionEntity,
    AdministrativeDivisionLegalCodeEntity,
)
from core.domains.house.enum.house_enum import DivisionLevelEnum


class AdministrativeDivisionModel(db.Model):
    __tablename__ = "administrative_divisions"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )

    name = Column(String(100), nullable=False)
    short_name = Column(String(30), nullable=False)
    apt_trade_price = Column(Integer, nullable=False)
    apt_deposit_price = Column(Integer, nullable=False)
    op_trade_price = Column(Integer, nullable=False)
    op_deposit_price = Column(Integer, nullable=False)
    public_sale_price = Column(Integer, nullable=False)
    front_legal_code = Column(String(5), nullable=False, unique=False, index=True)
    back_legal_code = Column(String(5), nullable=False, unique=False, index=True)
    level = Column(
        Enum(DivisionLevelEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    coordinates = Column(
        Geometry(geometry_type="POINT", srid=4326).with_variant(String, "sqlite"),
        nullable=True,
    )
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    name_ts = Column(TSVECTOR().with_variant(String(100), "sqlite"), nullable=True)

    latitude = column_property(coordinates.ST_Y())
    longitude = column_property(coordinates.ST_X())

    is_available = Column(Boolean, nullable=False, default=True)

    @property
    def apt_trade_visible(self):
        if self.apt_trade_price == 0:
            return False
        return True

    @property
    def apt_deposit_visible(self):
        if self.apt_deposit_price == 0:
            return False
        return True

    @property
    def op_trade_visible(self):
        if self.op_trade_price == 0:
            return False
        return True

    @property
    def op_deposit_visible(self):
        if self.op_deposit_price == 0:
            return False
        return True

    def to_entity(self) -> AdministrativeDivisionEntity:
        return AdministrativeDivisionEntity(
            id=self.id,
            name=self.name,
            short_name=self.short_name,
            apt_trade_price=self.apt_trade_price,
            apt_deposit_price=self.apt_deposit_price,
            op_trade_price=self.op_trade_price,
            op_deposit_price=self.op_deposit_price,
            public_sale_price=self.public_sale_price,
            level=self.level,
            latitude=self.latitude,
            longitude=self.longitude,
            is_available=self.is_available,
            front_legal_code=self.front_legal_code,
            back_legal_code=self.back_legal_code,
            created_at=self.created_at,
            updated_at=self.updated_at,
            apt_trade_visible=self.apt_trade_visible,
            apt_deposit_visible=self.apt_deposit_visible,
            op_trade_visible=self.op_trade_visible,
            op_deposit_visible=self.op_deposit_visible,
        )

    def to_legal_code_entity(self) -> AdministrativeDivisionLegalCodeEntity:
        return AdministrativeDivisionLegalCodeEntity(
            id=self.id,
            name=self.name,
            short_name=self.short_name,
            front_legal_code=self.front_legal_code,
            back_legal_code=self.back_legal_code,
        )
