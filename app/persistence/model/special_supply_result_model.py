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
from core.domains.house.entity.house_entity import SpecialSupplyResultReportEntity


class SpecialSupplyResultModel(db.Model):
    __tablename__ = "special_supply_results"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    public_sale_details_id = Column(
        BigInteger, ForeignKey(PublicSaleDetailModel.id), nullable=False, index=True,
    )

    region = Column(String(10), nullable=True)
    region_percent = Column(SmallInteger, nullable=True)
    multi_children_vol = Column(SmallInteger, nullable=True)
    newlywed_vol = Column(SmallInteger, nullable=True)
    old_parent_vol = Column(SmallInteger, nullable=True)
    first_life_vol = Column(SmallInteger, nullable=True)

    def to_report_entity(self) -> SpecialSupplyResultReportEntity:
        total_vol = 0
        if isinstance(self.multi_children_vol, int):
            total_vol += total_vol + self.multi_children_vol
        if isinstance(self.newlywed_vol, int):
            total_vol += total_vol + self.newlywed_vol
        if isinstance(self.old_parent_vol, int):
            total_vol += total_vol + self.old_parent_vol
        if isinstance(self.first_life_vol, int):
            total_vol += total_vol + self.first_life_vol

        return SpecialSupplyResultReportEntity(
            region=self.region,
            region_percent=self.region_percent,
            multi_children_vol=self.multi_children_vol,
            newlywed_vol=self.newlywed_vol,
            old_parent_vol=self.old_parent_vol,
            first_life_vol=self.first_life_vol,
            total_vol=total_vol,
        )
