from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp


class UserModel(db.Model):
    __tablename__ = "users"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    is_home_owner = Column(Boolean, nullable=True)
    interested_house_type = Column(
        String(10), nullable=True
    )
    is_active = Column(Boolean, nullable=False, default=True)
    is_out = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=get_server_timestamp())
    updated_at = Column(DateTime, default=get_server_timestamp())

    interest_regions = relationship("InterestRegionModel", backref=backref("users"))
    devices = relationship("DeviceModel", backref=backref("users"))
