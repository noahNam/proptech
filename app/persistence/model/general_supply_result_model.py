from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    String,
    SmallInteger,
    UniqueConstraint,
)

from app import db
from app.persistence.model.public_sale_detail_model import PublicSaleDetailModel
from core.domains.house.entity.house_entity import GeneralSupplyResultReportEntity


class GeneralSupplyResultModel(db.Model):
    __tablename__ = "general_supply_results"
    __table_args__ = (UniqueConstraint("public_sale_details_id", "region"),)

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    public_sale_details_id = Column(
        BigInteger,
        ForeignKey(PublicSaleDetailModel.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    region = Column(String(10), nullable=True)
    region_percent = Column(SmallInteger, nullable=True)
    applicant_num = Column(Integer, nullable=True)
    competition_rate = Column(SmallInteger, nullable=True)
    win_point = Column(SmallInteger, nullable=True)

    def to_report_entity(self) -> GeneralSupplyResultReportEntity:
        return GeneralSupplyResultReportEntity(
            region=self.region,
            region_percent=self.region_percent,
            applicant_num=self.applicant_num,
            competition_rate=self.competition_rate,
            win_point=self.win_point,
        )
