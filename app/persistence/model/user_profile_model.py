from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    DateTime,
    Integer, ForeignKey, String,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import UserModel


class UserProfileModel(db.Model):
    __tablename__ = "user_profiles"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False, unique=True)
    nickname = Column(String(12), nullable=True)
    last_update_code = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    user_infos = relationship("UserInfoModel", backref=backref("user_profiles"))
