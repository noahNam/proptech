from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.persistence.model import UserModel
from core.domains.user.entity.user_entity import DeviceEntity


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
    phone_number = Column(String(75), nullable=True)
    endpoint = Column(String(100), nullable=True, default="")
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    device_token = relationship(
        "DeviceTokenModel", backref=backref("devices"), uselist=False
    )

    def to_entity(self) -> DeviceEntity:
        return DeviceEntity(
            id=self.id,
            user_id=self.user_id,
            uuid=self.uuid,
            os=self.os,
            is_active=self.is_active,
            is_auth=self.is_auth,
            phone_number=self.phone_number,
            endpoint=self.endpoint,
            created_at=self.created_at,
            updated_at=self.updated_at,
            device_token=self.device_token.to_entity() if self.device_token else None,
        )
