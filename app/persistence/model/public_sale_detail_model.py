from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    Float,
)

from app import db
from app.persistence.model.public_sale_model import PublicSaleModel
from core.domains.house.entity.house_entity import PublicSaleDetailEntity


class PublicSaleDetailModel(db.Model):
    __tablename__ = "public_sale_details"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    public_sales_id = Column(BigInteger,
                             ForeignKey(PublicSaleModel.id, ondelete="CASCADE"),
                             nullable=False)
    private_area = Column(Float, nullable=False)
    supply_area = Column(Float, nullable=False)
    supply_price = Column(Integer, nullable=False)
    acquisition_tax = Column(Integer, nullable=False)

    def to_entity(self) -> PublicSaleDetailEntity:
        return PublicSaleDetailEntity(
            id=self.id,
            public_sales_id=self.public_sales_id,
            private_area=self.private_area,
            supply_area=self.supply_area,
            supply_price=self.supply_price,
            acquisition_tax=self.acquisition_tax
        )
