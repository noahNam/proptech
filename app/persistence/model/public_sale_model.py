from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
    String, Date, SmallInteger,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.time_helper import get_server_timestamp
from app.persistence.model.real_estate_model import RealEstateModel
from core.domains.house.entity.house_entity import PublicSaleEntity
from core.domains.house.enum.house_enum import HousingCategoryEnum, RentTypeEnum, PreSaleTypeEnum


class PublicSaleModel(db.Model):
    __tablename__ = "public_sales"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    real_estate_id = Column(BigInteger,
                            ForeignKey(RealEstateModel.id, ondelete="CASCADE"),
                            nullable=False)
    name = Column(String(50), nullable=False)
    region = Column(String(20), nullable=False)
    housing_category = Column(Enum(HousingCategoryEnum, values_callable=lambda obj: [e.value for e in obj]),
                              nullable=False)
    rent_type = Column(Enum(RentTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
                       nullable=False)
    trade_type = Column(Enum(PreSaleTypeEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    construct_company = Column(String(30), nullable=True)
    supply_household = Column(Integer, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
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
    min_down_payment = Column(Integer, nullable=False)
    max_down_payment = Column(Integer, nullable=False)
    down_payment_ratio = Column(Integer, nullable=False)
    reference_url = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=get_server_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=get_server_timestamp(), nullable=False)

    # 1:1 relationship
    public_sale_photos = relationship("PublicSalePhotoModel",
                                      backref=backref("public_sales"),
                                      uselist=False)
    public_sale_details = relationship("PuvlicSaleDetailModel",
                                       backref=backref("public_sales",
                                                       cascade="all, delete"))

    def __repr__(self):
        return (
            f"PublicSale({self.id}, "
            f"{self.real_estate_id}, "
            f"{self.name}, "
            f"{self.region}, "
            f"{self.housing_category}, "
            f"{self.rent_type}, "
            f"{self.trade_type}, "
            f"{self.construct_company}, "
            f"{self.supply_household}, "
            f"{self.is_available}, "
            f"{self.offer_date}, "
            f"{self.subscription_start_date}, "
            f"{self.subscription_end_date}, "
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
            f"{self.move_in_month}, "
            f"{self.min_down_payment}, "
            f"{self.max_down_payment}, "
            f"{self.down_payment_ratio}, "
            f"{self.reference_url}, "
            f"{self.created_at}, "
            f"{self.updated_at})"
        )

    def to_entity(self) -> PublicSaleEntity:
        return PublicSaleEntity(
            id=self.id,
            real_estate_id=self.real_estate_id,
            name=self.name,
            region=self.region,
            housing_category=self.housing_category,
            rent_type=self.rent_type,
            trade_type=self.trade_price,
            construct_company=self.construct_company,
            supply_household=self.supply_household,
            is_available=self.is_available,
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
            move_in_month=self.move_in_month,
            min_down_payment=self.min_down_payment,
            max_down_payment=self.max_down_payment,
            down_payment_ratio=self.down_payment_ratio,
            reference_url=self.reference_url,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
