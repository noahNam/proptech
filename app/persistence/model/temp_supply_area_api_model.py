from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Float,
    DateTime,
    func,
    SmallInteger,
)
from app import db


# todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
class TempSupplyAreaApiModel(db.Model):
    __tablename__ = "temp_supply_area_api"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    req_front_legal_code = Column(String(5), nullable=True)
    req_back_legal_code = Column(String(5), nullable=True)
    req_land_number = Column(String(10), nullable=True)
    req_real_estate_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=True
    )
    req_real_estate_name = Column(String(50), nullable=True)
    req_private_sales_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=True
    )
    req_private_sale_name = Column(String(50), nullable=True)
    req_jibun_address = Column(String(100), nullable=True)
    req_road_address = Column(String(100), nullable=True)
    resp_rnum = Column(Integer(), nullable=True)
    resp_total_count = Column(Integer(), nullable=True)
    resp_name = Column(String(50), nullable=True)
    resp_dong_nm = Column(String(50), nullable=True)
    resp_ho_nm = Column(String(50), nullable=True)
    resp_flr_no_nm = Column(String(50), nullable=True)
    resp_area = Column(Float(), nullable=True)
    resp_jibun_address = Column(String(100), nullable=True)
    resp_road_address = Column(String(100), nullable=True)
    resp_etc_purps = Column(String(50), nullable=True)
    resp_expos_pubuse_gb_cd_nm = Column(String(2), nullable=True)
    resp_main_atch_gb_cd = Column(SmallInteger(), nullable=True)
    resp_main_atch_gb_cd_nm = Column(String(10), nullable=True)
    resp_main_purps_cd = Column(String(5), nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )
