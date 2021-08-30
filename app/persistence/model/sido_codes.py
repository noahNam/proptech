from sqlalchemy import Column, BigInteger, Integer, String

from app import db
from core.domains.user.entity.user_entity import SidoCodeEntity


class SidoCodeModel(db.Model):
    __tablename__ = "sido_codes"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    sido_code = Column(Integer, nullable=False)
    sido_name = Column(String(10), nullable=False)
    sigugun_code = Column(Integer, nullable=False)
    sigugun_name = Column(String(10), nullable=False)

    def to_entity(self) -> SidoCodeEntity:
        return SidoCodeEntity(
            id=self.id,
            sido_name=self.sido_name,
            sigugun_name=self.sigugun_name,
        )
