from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    ForeignKey,
    String,
    SmallInteger,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model import UserModel
from core.domains.user.entity.user_entity import UserProfileEntity


class UserProfileModel(db.Model):
    __tablename__ = "user_profiles"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False, unique=True)
    nickname = Column(String(12), nullable=True)
    last_update_code = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    user_infos = relationship("UserInfoModel", backref=backref("user_profiles"))

    def to_entity(self) -> UserProfileEntity:
        return UserProfileEntity(
            id=self.id,
            user_id=self.user_id,
            nickname=self.nickname,
            last_update_code=self.last_update_code,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
