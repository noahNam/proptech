from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.user_model import UserModel
from core.domains.notification.entity.notification_entity import ReceivePushTypeEntity


class ReceivePushTypeModel(db.Model):
    __tablename__ = "receive_push_types"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False, unique=True, index=True,)
    is_official = Column(Boolean, nullable=False, default=True)
    is_private = Column(Boolean, nullable=False, default=True)
    is_marketing = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime, default=get_server_timestamp())

    def to_entity(self) -> ReceivePushTypeEntity:
        return ReceivePushTypeEntity(
            id=self.id,
            user_id=self.user_id,
            is_official=self.is_official,
            is_private=self.is_private,
            is_marketing=self.is_marketing,
            updated_at=self.updated_at,
        )
