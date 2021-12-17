from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
    String,
    SmallInteger,
    func,
    Float,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, backref

from app import db
from app.extensions.utils.house_helper import HouseHelper
from app.persistence.model.real_estate_model import RealEstateModel
from core.domains.house.entity.house_entity import (
    PublicSaleEntity,
    PublicSalePushEntity,
    PublicSaleDetailCalendarEntity,
    PublicSaleReportEntity,
)
from core.domains.house.enum.house_enum import (
    RentTypeEnum,
    PreSaleTypeEnum,
)


class PublicSaleModel(db.Model):
    __tablename__ = "public_sales"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    real_estate_id = Column(
        BigInteger,
        ForeignKey(RealEstateModel.id),
        nullable=False,
        unique=True,
        index=True,
    )
    name = Column(String(150), nullable=False)
    region = Column(String(20), nullable=False)
    housing_category = Column(String(2), nullable=False,)
    rent_type = Column(
        Enum(RentTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    trade_type = Column(
        Enum(PreSaleTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    construct_company = Column(String(50), nullable=True)
    supply_household = Column(Integer, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    offer_date = Column(String(8), nullable=True)
    subscription_start_date = Column(String(8), nullable=True)
    subscription_end_date = Column(String(8), nullable=True)
    special_supply_date = Column(String(8), nullable=True)
    special_supply_etc_date = Column(String(8), nullable=True)
    special_etc_gyeonggi_date = Column(String(8), nullable=True)
    first_supply_date = Column(String(8), nullable=True)
    first_supply_etc_date = Column(String(8), nullable=True)
    first_etc_gyeonggi_date = Column(String(8), nullable=True)
    second_supply_date = Column(String(8), nullable=True)
    second_supply_etc_date = Column(String(8), nullable=True)
    second_etc_gyeonggi_date = Column(String(8), nullable=True)
    notice_winner_date = Column(String(8), nullable=True)
    contract_start_date = Column(String(8), nullable=True)
    contract_end_date = Column(String(8), nullable=True)
    move_in_year = Column(SmallInteger, nullable=True)
    move_in_month = Column(SmallInteger, nullable=True)
    min_down_payment = Column(Integer, nullable=False)
    max_down_payment = Column(Integer, nullable=False)
    down_payment_ratio = Column(Integer, nullable=False)
    reference_url = Column(String(50), nullable=True)
    offer_notice_url = Column(String(100), nullable=True)

    heating_type = Column(String(100), nullable=True)
    floor_area_ratio = Column(Float(), nullable=True)
    building_cover_ratio = Column(Float(), nullable=True)
    total_household = Column(Integer, nullable=True)
    total_park_number = Column(Integer, nullable=True)
    top_floor = Column(SmallInteger, nullable=True)
    dong_number = Column(Integer, nullable=True)
    contract_amount = Column(Float(), nullable=True)
    middle_amount = Column(Float(), nullable=True)
    remain_amount = Column(Float(), nullable=True)
    sale_limit = Column(String(100), nullable=True)
    compulsory_residence = Column(String(100), nullable=True)

    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    name_ts = Column(TSVECTOR().with_variant(String(150), "sqlite"), nullable=True)

    # 1:M relationship
    public_sale_photos = relationship(
        "PublicSalePhotoModel", backref=backref("public_sales"), uselist=True
    )
    public_sale_details = relationship(
        "PublicSaleDetailModel", backref=backref("public_sales")
    )

    public_sale_avg_prices = relationship(
        "PublicSaleAvgPriceModel",
        backref=backref("public_sale_avg_prices"),
        uselist=True,
        primaryjoin="foreign(PublicSaleModel.id)== PublicSaleAvgPriceModel.public_sales_id",
        viewonly=True,
    )

    def to_entity(self) -> PublicSaleEntity:
        return PublicSaleEntity(
            id=self.id,
            real_estate_id=self.real_estate_id,
            name=self.name,
            region=self.region,
            housing_category=self.housing_category,
            rent_type=self.rent_type,
            trade_type=self.trade_type,
            construct_company=self.construct_company,
            supply_household=self.supply_household,
            is_available=self.is_available,
            offer_date=self.offer_date,
            subscription_start_date=self.subscription_start_date,
            subscription_end_date=self.subscription_end_date,
            status=HouseHelper().public_status(
                offer_date=self.offer_date,
                subscription_end_date=self.subscription_end_date,
            ),
            special_supply_date=self.special_supply_date,
            special_supply_etc_date=self.special_supply_etc_date,
            special_etc_gyeonggi_date=self.special_etc_gyeonggi_date,
            first_supply_date=self.first_supply_date,
            first_supply_etc_date=self.first_supply_etc_date,
            first_etc_gyeonggi_date=self.first_etc_gyeonggi_date,
            second_supply_date=self.second_supply_date,
            second_supply_etc_date=self.second_supply_etc_date,
            second_etc_gyeonggi_date=self.second_etc_gyeonggi_date,
            notice_winner_date=self.notice_winner_date,
            contract_start_date=self.contract_start_date,
            contract_end_date=self.contract_end_date,
            move_in_year=self.move_in_year,
            move_in_month=self.move_in_month,
            min_down_payment=self.min_down_payment,
            max_down_payment=self.max_down_payment,
            down_payment_ratio=self.down_payment_ratio,
            reference_url=self.reference_url,
            offer_notice_url=self.offer_notice_url,
            total_household=self.total_household,
            total_park_number=self.total_park_number,
            top_floor=self.top_floor,
            dong_number=self.dong_number,
            contract_amount=HouseHelper.convert_contract_amount_to_integer(
                self.contract_amount
            ),
            middle_amount=self.middle_amount,
            remain_amount=self.remain_amount,
            sale_limit=self.sale_limit,
            created_at=self.created_at,
            updated_at=self.updated_at,
            public_sale_photos=[
                public_sale_photo.to_entity()
                for public_sale_photo in self.public_sale_photos
            ]
            if self.public_sale_photos
            else None,
            public_sale_details=[
                public_sale_detail.to_entity()
                for public_sale_detail in self.public_sale_details
            ]
            if self.public_sale_details
            else None,
        )

    def to_push_entity(self, message_type: str) -> PublicSalePushEntity:
        return PublicSalePushEntity(
            id=self.id, name=self.name, region=self.region, message_type=message_type,
        )

    def to_calendar_entity(self) -> PublicSaleDetailCalendarEntity:
        return PublicSaleDetailCalendarEntity(
            id=self.id,
            real_estate_id=self.real_estate_id,
            name=self.name,
            trade_type=self.trade_type,
            offer_date=self.offer_date,
            subscription_start_date=self.subscription_start_date,
            subscription_end_date=self.subscription_end_date,
            special_supply_date=self.special_supply_date,
            special_supply_etc_date=self.special_supply_etc_date,
            special_etc_gyeonggi_date=self.special_etc_gyeonggi_date,
            first_supply_date=self.first_supply_date,
            first_supply_etc_date=self.first_supply_etc_date,
            first_etc_gyeonggi_date=self.first_etc_gyeonggi_date,
            second_supply_date=self.second_supply_date,
            second_supply_etc_date=self.second_supply_etc_date,
            second_etc_gyeonggi_date=self.second_etc_gyeonggi_date,
            notice_winner_date=self.notice_winner_date,
            contract_start_date=self.contract_start_date,
            contract_end_date=self.contract_end_date,
            move_in_year=self.move_in_year,
            move_in_month=self.move_in_month,
        )

    def to_report_entity(self) -> PublicSaleReportEntity:
        return PublicSaleReportEntity(
            id=self.id,
            name=self.name,
            real_estate_id=self.real_estate_id,
            supply_household=self.supply_household,
            offer_date=self.offer_date,
            special_supply_date=self.special_supply_date,
            special_supply_etc_date=self.special_supply_etc_date,
            special_etc_gyeonggi_date=self.special_etc_gyeonggi_date,
            first_supply_date=self.first_supply_date,
            first_supply_etc_date=self.first_supply_etc_date,
            first_etc_gyeonggi_date=self.first_etc_gyeonggi_date,
            second_supply_date=self.second_supply_date,
            second_supply_etc_date=self.second_supply_etc_date,
            second_etc_gyeonggi_date=self.second_etc_gyeonggi_date,
            notice_winner_date=self.notice_winner_date,
            public_sale_photos=[
                public_sale_photo.to_entity()
                for public_sale_photo in self.public_sale_photos
            ]
            if self.public_sale_photos
            else None,
            public_sale_details=[
                public_sale_detail.to_report_entity()
                for public_sale_detail in self.public_sale_details
            ]
            if self.public_sale_details
            else None,
            real_estates=self.real_estates.to_report_entity(),
        )
