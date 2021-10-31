from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    ForeignKey,
)

from app import db
from app.persistence.model.device_model import DeviceModel
from core.domains.user.entity.user_entity import DeviceTokenEntity


class DeviceTokenModel(db.Model):
    __tablename__ = "device_tokens"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    device_id = Column(
        BigInteger, ForeignKey(DeviceModel.id), nullable=False, unique=True, index=True,
    )
    token = Column(String(163), nullable=False)

    def to_entity(self) -> DeviceTokenEntity:
        return DeviceTokenEntity(
            id=self.id, device_id=self.device_id, token=self.token,
        )
