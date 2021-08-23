from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    String,
    SmallInteger,
)

from app import db
from app.persistence.model.public_sale_detail_model import PublicSaleDetailModel


class SpecialSupplyResultModel(db.Model):
    __tablename__ = "special_supply_results"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    public_sale_details_id = Column(
        BigInteger,
        ForeignKey(PublicSaleDetailModel.id, ondelete="CASCADE"),
        nullable=False,
    )

    region = Column(String(10), nullable=True)
    region_percent = Column(SmallInteger, nullable=True)
    multi_children_vol = Column(SmallInteger, nullable=True)
    newlywed_vol = Column(SmallInteger, nullable=True)
    old_parent_vol = Column(SmallInteger, nullable=True)
    first_life_vol = Column(SmallInteger, nullable=True)
