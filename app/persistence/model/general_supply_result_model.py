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


class GeneralSupplyResultModel(db.Model):
    __tablename__ = "general_supply_results"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    public_sale_details_id = Column(
        BigInteger,
        ForeignKey(PublicSaleDetailModel.id, ondelete="CASCADE"),
        nullable=False,
    )

    region = Column(String(10), nullable=True)
    region_percent = Column(SmallInteger, nullable=True)
    applicant_num = Column(SmallInteger, nullable=True)
    competition_rate = Column(SmallInteger, nullable=True)
    win_point = Column(SmallInteger, nullable=True)
