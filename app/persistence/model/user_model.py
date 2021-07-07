from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    DateTime,
    Integer, String,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.user.entity.user_entity import UserEntity


class UserModel(db.Model):
    __tablename__ = "users"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    is_required_agree_terms = Column(Boolean, nullable=False, default=False)
    join_date = Column(String(8), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_out = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=get_server_timestamp())
    updated_at = Column(DateTime, default=get_server_timestamp())

    devices = relationship("DeviceModel", backref=backref("users"), uselist=False)
    user_profiles = relationship(
        "UserProfileModel", backref=backref("users"), uselist=False
    )
    receive_push_types = relationship(
        "ReceivePushTypeModel", backref=backref("users"), uselist=False
    )

    def to_entity(self) -> UserEntity:
        return UserEntity(
            id=self.id,
            is_required_agree_terms=self.is_required_agree_terms,
            join_date=self.join_date,
            is_active=self.is_active,
            is_out=self.is_out,
        )
