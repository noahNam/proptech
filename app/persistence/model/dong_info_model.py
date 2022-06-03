from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Numeric, DateTime, func,
)
from sqlalchemy.orm import relationship

from app import db
from core.domains.house.entity.house_entity import DongInfoEntity


class DongInfoModel(db.Model):
    __tablename__ = "dong_infos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    private_sale_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )
    name = Column(String(30), nullable=True)
    hhld_cnt = Column(Numeric(5), nullable=True)
    grnd_flr_cnt = Column(Numeric(5), nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # relationship
    type_infos = relationship(
        "TypeInfoModel", backref="dong_infos", uselist=True, primaryjoin="DongInfoModel.id == foreign(TypeInfoModel.dong_id)",
    )

    def to_entity(self) -> DongInfoEntity:
        return DongInfoEntity(
            id=self.id,
            private_sale_id=self.private_sale_id,
            name=self.name,
            hhld_cnt=self.hhld_cnt,
            grnd_flr_cnt=self.grnd_flr_cnt,
            created_at=self.created_at,
            updated_at=self.updated_at,
            type_infos=[
                type_info.to_entity()
                for type_info in self.type_infos
            ]
            if self.type_infos
            else None,
        )