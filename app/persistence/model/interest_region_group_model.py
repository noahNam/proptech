from sqlalchemy import Column, BigInteger, Integer, String, SmallInteger

from app import db


class InterestRegionGroupModel(db.Model):
    __tablename__ = "interest_region_groups"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    level = Column(SmallInteger, nullable=False, default=0)
    name = Column(String(20), nullable=False)
    interest_count = Column(Integer, nullable=False, default=0)
