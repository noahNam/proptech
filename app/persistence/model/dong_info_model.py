from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    String,
    SmallInteger,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.persistence.model import PrivateSaleModel


class DongInfoModel(db.Model):
    __tablename__ = "dong_infos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    private_sales_id = Column(
        BigInteger,
        ForeignKey(PrivateSaleModel.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dong = Column(String(10), nullable=True)
    floor = Column(SmallInteger, nullable=True)
    structure_type = Column(String(3), nullable=True)

    room_infos = relationship(
        "RoomInfoModel", backref=backref("dong_infos", cascade="all, delete"),
    )
