from sqlalchemy import Column, BigInteger, Integer, String, DateTime

from app import db
from app.extensions.utils.time_helper import get_server_timestamp


class UserStatsLogModel(db.Model):
    __tablename__ = "user_status_logs"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True
    )
    user_id = Column(BigInteger, nullable=False)
    status = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=get_server_timestamp())
