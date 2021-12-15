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
    func,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.persistence.model.real_estate_model import RealEstateModel
from core.domains.house.entity.house_entity import PrivateSaleEntity
from core.domains.house.enum.house_enum import BuildTypeEnum


class PrivateSaleModel(db.Model):
    __tablename__ = "private_sales"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    real_estate_id = Column(
        BigInteger,
        ForeignKey(RealEstateModel.id),
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
    move_in_year = Column(String(6), nullable=True)
    construct_company = Column(String(30), nullable=True)
    dong_num = Column(SmallInteger, nullable=True)
    park_space_num = Column(Float, nullable=True)
    heating_type = Column(String(10), nullable=True)
    floor_area_ratio = Column(SmallInteger, nullable=True)
    building_cover_ratio = Column(SmallInteger, nullable=True)
    trade_status = Column(SmallInteger, nullable=False, default=0)
    deposit_status = Column(SmallInteger, nullable=False, default=0)
    public_ref_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_available = Column(Boolean, nullable=False, default=False)

    private_sale_details = relationship(
        "PrivateSaleDetailModel", backref=backref("private_sales"),
    )

    dong_infos = relationship("DongInfoModel", backref=backref("private_sales"),)

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
