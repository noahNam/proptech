from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
)

from app import db


class AvgMonthlyIncomeWokrerModel(db.Model):
    __tablename__ = "avg_monthly_income_workers"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False
    )
    year = Column(String(4), nullable=False)
    three = Column(Integer, nullable=False)
    four = Column(Integer, nullable=False)
    five = Column(Integer, nullable=False)
    six = Column(Integer, nullable=False)
    seven = Column(Integer, nullable=False)
    eight = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False)
