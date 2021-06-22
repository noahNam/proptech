from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.notification.enum.notification_enum import NotificationStatusEnum


class NotificationModel(db.Model):
    __tablename__ = "notifications"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, nullable=False)
    token = Column(String(163), nullable=False)
    endpoint = Column(String(100), nullable=True, default="")
    category = Column(String(6), nullable=False)
    data = Column(
        "data", JSONB().with_variant(JSON, "sqlite"), nullable=False, default={}
    )
    is_read = Column("is_read", Boolean, nullable=False, default=False)
    is_pending = Column("is_pending", Boolean, nullable=False, default=True)
    status = Column(
        String(10), nullable=True, default=NotificationStatusEnum.WAIT.value
    )
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
