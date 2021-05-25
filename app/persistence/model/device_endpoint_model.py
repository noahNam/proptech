from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    ForeignKey,
)

from app import db
from app.persistence.model.device_model import DeviceModel


class DeviceEndpointModel(db.Model):
    __tablename__ = "device_endpoints"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    device_id = Column(BigInteger, ForeignKey(DeviceModel.id), nullable=False)
    endpoint = Column(String(32), nullable=False)
