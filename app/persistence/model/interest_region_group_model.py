from sqlalchemy import Column, BigInteger, Integer, String

from app import db


class InterestRegionGroupModel(db.Model):
    __tablename__ = "interest_region_groups"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    name = Column(String(20), nullable=False)
    interest_count = Column(Integer, nullable=False, default=0)
