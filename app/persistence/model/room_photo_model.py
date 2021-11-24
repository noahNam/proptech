from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    String,
    DateTime,
)

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.room_info_model import RoomInfoModel


class RoomPhotoModel(db.Model):
    __tablename__ = "room_photos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    room_info_id = Column(
        BigInteger,
        ForeignKey(RoomInfoModel.id),
        nullable=False,
        unique=True,
        index=True,
    )

    type = Column(String(3), nullable=False)
    file_name = Column(String(20), nullable=False)
    path = Column(String(150), nullable=False)
    extension = Column(String(4), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=get_server_timestamp(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=get_server_timestamp(), nullable=False
    )
