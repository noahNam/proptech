from sqlalchemy import Column, BigInteger, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.user.enum.user_enum import UserDefaultValueEnum


class UserModel(db.Model):
    __tablename__ = "users"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
    )
    nickname = Column(String(20), nullable=False, default=UserDefaultValueEnum.NICKNAME.value)
    email = Column(String(40), nullable=True)
    birthday = Column(String(8), nullable=True)
    gender = Column(String(1), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_out = Column(Boolean, nullable=False, default=False)
    profile_img_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp())
    updated_at = Column(DateTime, default=get_server_timestamp())

    interest_regions = relationship(
        "InterestRegionModel", backref=backref("users")
    )
