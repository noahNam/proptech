from sqlalchemy import (
    Column,
    BigInteger,
    DateTime,
    Integer, ForeignKey, String, SmallInteger,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.user_profile_model import UserProfileModel


class UserInfoModel(db.Model):
    __tablename__ = "user_infos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_profile_id = Column(BigInteger, ForeignKey(UserProfileModel.id), nullable=False)
    code = Column(SmallInteger, nullable=True)
    value = Column(String(8), nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
