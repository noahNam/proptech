from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Float,
    DateTime,
    func,
    Text,
    Boolean,
)
from app import db


from core.domains.house.entity.house_entity import BindFailureSupplyAreaEntity


# todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
class TempFailureSupplyAreaModel(db.Model):
    __tablename__ = "temp_failure_supply_area"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    real_estate_name = Column(String(50), nullable=True)
    private_sale_name = Column(String(50), nullable=True)
    real_estate_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=True)
    private_sale_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=True
    )

    private_area = Column(Float(), nullable=True)
    supply_area = Column(Float(), nullable=True)
    front_legal_code = Column(String(5), nullable=True)
    back_legal_code = Column(String(5), nullable=True)
    jibun_address = Column(String(100), nullable=True)
    road_address = Column(String(100), nullable=True)
    land_number = Column(String(10), nullable=True)
    failure_reason = Column(Text(), nullable=True)
    is_done = Column(Boolean(), nullable=True)
    ref_summary_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> BindFailureSupplyAreaEntity:
        return BindFailureSupplyAreaEntity(
            id=self.id,
            real_estate_name=self.real_estate_name,
            private_sale_name=self.private_sale_name,
            real_estate_id=self.real_estate_id,
            private_sale_id=self.private_sale_id,
            private_area=self.private_area,
            supply_area=self.supply_area,
            front_legal_code=self.front_legal_code,
            back_legal_code=self.back_legal_code,
            jibun_address=self.jibun_address,
            road_address=self.road_address,
            land_number=self.land_number,
            failure_reason=self.failure_reason,
            is_done=self.is_done,
            ref_summary_id=self.ref_summary_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
