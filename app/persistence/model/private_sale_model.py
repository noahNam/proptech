from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    DateTime,
    Enum,
    String,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.real_estate_model import RealEstateModel
from core.domains.house.entity.house_entity import PrivateSaleEntity
from core.domains.house.enum.house_enum import BuildTypeEnum


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
    name = Column(String(50), nullable=True)
    building_type = Column(Enum(BuildTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
                           nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    private_sale_details = relationship("PrivateSaleDetailModel",
                                        backref=backref("private_sales", cascade="all, delete"))

    def to_entity(self) -> PrivateSaleEntity:
        return PrivateSaleEntity(
            id=self.id,
            real_estate_id=self.real_estate_id,
            building_type=self.building_type,
            private_sale_details=[private_sale_details.to_entity() for private_sale_details in
                                  self.private_sale_details] if self.private_sale_details else None,
            created_at=self.created_at.date().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.date().strftime("%Y-%m-%d %H:%M:%S")
        )
