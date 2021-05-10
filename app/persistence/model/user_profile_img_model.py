from sqlalchemy import Column, BigInteger, Integer, String, Boolean, DateTime

from app import db
from app.extensions.utils.time_helper import get_server_timestamp


class UserProfileImgModel(db.Model):
    __tablename__ = "user_profile_imgs"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    file_name = Column(String(50), nullable=True)
    uuid = Column(String(100), nullable=True)
    path = Column(String(100), nullable=True)
    extension = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp())
    updated_at = Column(DateTime, default=get_server_timestamp())
