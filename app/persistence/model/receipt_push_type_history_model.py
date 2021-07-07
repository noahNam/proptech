from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime, Boolean, String,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp


class ReceivePushTypeHistoryModel(db.Model):
    __tablename__ = "receive_push_type_histories"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    user_id = Column(BigInteger, nullable=False)
    push_type = Column(String(9), nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp())
