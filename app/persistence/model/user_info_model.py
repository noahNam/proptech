from sqlalchemy import (
    Column,
    BigInteger,
    DateTime,
    Integer,
    ForeignKey,
    String,
    SmallInteger,
    UniqueConstraint,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.user_profile_model import UserProfileModel
from core.domains.user.entity.user_entity import (
    UserInfoEntity,
    UserInfoResultEntity,
)


class UserInfoModel(db.Model):
    __tablename__ = "user_infos"
    __table_args__ = (UniqueConstraint("user_profile_id", "code"),)

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_profile_id = Column(
        BigInteger, ForeignKey(UserProfileModel.id), nullable=False
    )
    code = Column(SmallInteger, nullable=True)
    value = Column(String(8), nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    def to_entity(self) -> UserInfoEntity:
        return UserInfoEntity(
            user_profile_id=self.user_profile_id, code=self.code, value=self.value,
        )

    def to_result_entity(self) -> UserInfoResultEntity:
        return UserInfoResultEntity(code=self.code, user_value=self.value,)
