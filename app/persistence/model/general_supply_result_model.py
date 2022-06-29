from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    UniqueConstraint,
    DateTime,
    func,
    SmallInteger,
)

from app import db
from core.domains.house.entity.house_entity import GeneralSupplyResultReportEntity


class GeneralSupplyResultModel(db.Model):
    __tablename__ = "general_supply_results"
    __table_args__ = (UniqueConstraint("public_sale_detail_id", "region"),)

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    public_sale_detail_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )

    region = Column(String(10), nullable=True)
    region_percent = Column(SmallInteger, nullable=True)
    applicant_num = Column(SmallInteger, nullable=True)
    competition_rate = Column(SmallInteger, nullable=True)
    win_point = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_report_entity(self) -> GeneralSupplyResultReportEntity:
        return GeneralSupplyResultReportEntity(
            region=self.region,
            region_percent=self.region_percent,
            applicant_num=self.applicant_num,
            competition_rate=self.competition_rate,
            win_point=self.win_point,
        )
