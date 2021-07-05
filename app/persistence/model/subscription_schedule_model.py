from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    SmallInteger,
    Date,
)

from app import db
from app.persistence.model.pre_sale_model import PreSaleModel
from core.domains.map.entity.map_entity import SubscriptionScheduleEntity


class SubscriptionScheduleModel(db.Model):
    __tablename__ = "subscription_schedules"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    pre_sales_id = Column(BigInteger,
                          ForeignKey(PreSaleModel.id, ondelete="CASCADE"),
                          nullable=False,
                          unique=True)
    offer_date = Column(Date, nullable=False)
    subscription_start_date = Column(Date, nullable=False)
    subscription_end_date = Column(Date, nullable=False)
    special_supply_date = Column(Date, nullable=False)
    special_supply_etc_date = Column(Date, nullable=False)
    first_supply_date = Column(Date, nullable=False)
    first_supply_etc_date = Column(Date, nullable=False)
    second_supply_date = Column(Date, nullable=False)
    second_supply_etc_date = Column(Date, nullable=False)
    notice_winner_date = Column(Date, nullable=False)
    contract_start_date = Column(Date, nullable=False)
    contract_end_date = Column(Date, nullable=False)
    move_in_year = Column(SmallInteger, nullable=False)
    move_in_month = Column(SmallInteger, nullable=False)

    def __repr__(self):
        return (
            f"SubscriptionSchedule({self.id}', "
            f"{self.pre_sales_id}', "
            f"{self.offer_date}', "
            f"{self.subscription_start_date}', "
            f"{self.subscription_end_date}', "
            f"{self.special_supply_date}, "
            f"{self.special_supply_etc_date}, "
            f"{self.first_supply_date}, "
            f"{self.first_supply_etc_date}, "
            f"{self.second_supply_date}, "
            f"{self.second_supply_etc_date}, "
            f"{self.notice_winner_date}, "
            f"{self.contract_start_date}, "
            f"{self.contract_end_date}, "
            f"{self.move_in_year}, "
            f"{self.move_in_month})"
        )

    def to_entity(self) -> SubscriptionScheduleEntity:
        return SubscriptionScheduleEntity(
            id=self.id,
            pre_sales_id=self.pre_sales_id,
            offer_date=self.offer_date,
            subscription_start_date=self.subscription_start_date,
            subscription_end_date=self.subscription_end_date,
            special_supply_date=self.special_supply_date,
            special_supply_etc_date=self.special_supply_etc_date,
            first_supply_date=self.first_supply_date,
            first_supply_etc_date=self.first_supply_etc_date,
            second_supply_date=self.second_supply_date,
            second_supply_etc_date=self.second_supply_etc_date,
            notice_winner_date=self.notice_winner_date,
            contract_start_date=self.contract_start_date,
            contract_end_date=self.contract_end_date,
            move_in_year=self.move_in_year,
            move_in_month=self.move_in_month
        )
