from sqlalchemy import Column, BigInteger, Integer, String, Boolean, ForeignKey, SmallInteger, DateTime

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.user_model import UserModel


class InterestRegionModel(db.Model):
    __tablename__ = "interest_regions"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
    )
    user_id = Column(BigInteger, ForeignKey(UserModel.id), nullable=False)
    region_id = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp())
    updated_at = Column(DateTime, default=get_server_timestamp())
