from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    UniqueConstraint, Numeric, DateTime, func,
)

from app import db
from core.domains.house.entity.house_entity import SpecialSupplyResultReportEntity


class SpecialSupplyResultModel(db.Model):
    __tablename__ = "special_supply_results"
    __table_args__ = (UniqueConstraint("public_sale_detail_id", "region"),)

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    public_sale_detail_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )

    region = Column(String(10), nullable=True)
    region_percent = Column(Numeric(3), nullable=True)
    multi_children_vol = Column(Numeric(5), nullable=True)
    newlywed_vol = Column(Numeric(5), nullable=True)
    old_parent_vol = Column(Numeric(5), nullable=True)
    first_life_vol = Column(Numeric(5), nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

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
