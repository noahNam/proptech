from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    String,
    SmallInteger,
    Float,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.persistence.model.dong_info_model import DongInfoModel


class RoomInfoModel(db.Model):
    __tablename__ = "room_infos"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    dong_info_id = Column(
        BigInteger, ForeignKey(DongInfoModel.id), nullable=False, index=True,
    )
    area_type = Column(String(5), nullable=True)
    private_area = Column(Float, nullable=True)
    supply_area = Column(Float, nullable=True)
    registration_tax = Column(SmallInteger, nullable=True)
    holding_tax = Column(SmallInteger, nullable=True)
    multi_house_tax = Column(SmallInteger, nullable=True)
    changing_tax = Column(SmallInteger, nullable=True)
    winter_administration_cost = Column(SmallInteger, nullable=True)
    summer_administration_cost = Column(SmallInteger, nullable=True)

    room_photos = relationship("RoomPhotoModel", backref=backref("room_infos"),)
