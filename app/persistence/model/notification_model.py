from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
    SmallInteger,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

from app import db
from core.domains.notification.entity.notification_entity import NotificationEntity
from core.domains.notification.enum.notification_enum import NotificationStatusEnum


class NotificationModel(db.Model):
    __tablename__ = "notifications"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, nullable=False, index=True)
    token = Column(String(163), nullable=False)
    endpoint = Column(String(100), nullable=True, default="")
    uuid = Column(String(36), nullable=True)
    topic = Column(String(6), nullable=False, index=True)
    badge_type = Column(String(3), nullable=False)
    message = Column(
        "data", JSONB().with_variant(JSON, "sqlite"), nullable=False, default={}
    )
    is_read = Column("is_read", Boolean, nullable=False, default=False)
    is_pending = Column("is_pending", Boolean, nullable=False, default=True)
    status = Column(
        SmallInteger,
        nullable=False,
        default=NotificationStatusEnum.WAIT.value,
        index=True,
    )
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_entity(self) -> NotificationEntity:
        return NotificationEntity(
            id=self.id,
            user_id=self.user_id,
            token=self.token,
            endpoint=self.endpoint,
            uuid=self.uuid,
            topic=self.topic,
            badge_type=self.badge_type,
            message=self.message,
            is_read=self.is_read,
            is_pending=self.is_pending,
            status=self.status,
            created_at=self.created_at,
        )
