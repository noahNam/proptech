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


class NotificationModel(db.Model):
    __tablename__ = "notifications"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    user_id = Column(BigInteger, nullable=False)
    category = Column(String(6), nullable=False)
    data = Column(
        "data", JSONB().with_variant(JSON, "sqlite"), nullable=False, default={}
    )
    is_read = Column("is_read", Boolean, nullable=False, default=False)
    is_pending = Column("is_pending", Boolean, nullable=False, default=False)
    status = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp())
    updated_at = Column(DateTime, default=get_server_timestamp())
