from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Float,
    DateTime,
    func,
    Boolean,
)
from app import db


# todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
class TempSummarySupplyAreaApiModel(db.Model):
    __tablename__ = "temp_summary_supply_area_api"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    real_estate_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=True)
    real_estate_name = Column(String(50), nullable=True)
    private_sales_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=True
    )
    private_sale_name = Column(String(50), nullable=True)
    private_area = Column(Float(), nullable=True)
    supply_area = Column(Float(), nullable=True)
    success_yn = Column(Boolean(), nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )
