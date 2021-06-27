from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import UserModel


class DeviceModel(db.Model):
    __tablename__ = "devices"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False, unique=True)
    uuid = Column(String(36), nullable=False)
    os = Column(String(3), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_auth = Column(Boolean, nullable=False, default=False)
    phone_number = Column(String(11), nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    device_tokens = relationship(
        "DeviceTokenModel", backref=backref("devices"), uselist=False
    )
