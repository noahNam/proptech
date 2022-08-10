from typing import Optional, List

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    Boolean,
    String,
    func,
    Float,
    Numeric,
    SmallInteger,
)
from sqlalchemy.orm import relationship

from app import db
from app.extensions.utils.house_helper import HouseHelper
from app.extensions.utils.time_helper import get_server_timestamp
from core.domains.banner.entity.banner_entity import ButtonLinkEntity
from core.domains.house.entity.house_entity import (
    PublicSaleEntity,
    PublicSalePushEntity,
    PublicSaleDetailCalendarEntity,
    PublicSaleReportEntity,
    HousePublicDetailEntity,
)
from core.domains.report.entity.report_entity import (
    TicketUsageResultForHousePublicDetailEntity,
)


class PublicSaleModel(db.Model):
    __tablename__ = "public_sales"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    real_estate_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )
    name = Column(String(150), nullable=False)
    region = Column(String(20), nullable=False)
    housing_category = Column(String(2), nullable=False)
    rent_type = Column(String(10), nullable=False)
    trade_type = Column(String(5), nullable=False)
    construct_company = Column(String(50), nullable=True)
    supply_household = Column(SmallInteger, nullable=False)
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
    move_in_year = Column(String(4), nullable=True)
    move_in_month = Column(String(2), nullable=True)
    min_down_payment = Column(Integer, nullable=False)
    max_down_payment = Column(Integer, nullable=False)
    down_payment_ratio = Column(Integer, nullable=False)
    reference_url = Column(String(200), nullable=True)
    offer_notice_url = Column(String(100), nullable=True)
    heating_type = Column(String(10), nullable=True)
    vl_rat = Column(Numeric(6, 2), nullable=True)
    bc_rat = Column(Numeric(6, 2), nullable=True)
    hhld_total_cnt = Column(SmallInteger, nullable=True)
    park_total_cnt = Column(SmallInteger, nullable=True)
    highest_floor = Column(SmallInteger, nullable=True)
    dong_cnt = Column(SmallInteger, nullable=True)
    contract_amount = Column(Float(), nullable=True)
    middle_amount = Column(Float(), nullable=True)
    remain_amount = Column(Float(), nullable=True)
    sale_limit = Column(String(100), nullable=True)
    compulsory_residence = Column(String(100), nullable=True)
    hallway_type = Column(String(4), nullable=True)
    is_checked = Column(Boolean, nullable=False, default=False)
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # relationship
    public_sale_photos = relationship(
        "PublicSalePhotoModel",
        backref="public_sales",
        uselist=True,
        primaryjoin="PublicSaleModel.id == foreign(PublicSalePhotoModel.public_sale_id)",
    )
    public_sale_details = relationship(
        "PublicSaleDetailModel",
        backref="public_sales",
        uselist=True,
        primaryjoin="PublicSaleModel.id == foreign(PublicSaleDetailModel.public_sale_id)",
    )

    public_sale_avg_prices = relationship(
        "PublicSaleAvgPriceModel",
        backref="public_sale_avg_prices",
        uselist=True,
        primaryjoin="PublicSaleModel.id == foreign(PublicSaleAvgPriceModel.public_sale_id)",
    )

    @property
    def is_special_supply_finished(self) -> bool:
        result = False
        if not self.special_supply_etc_date:
            return result

        today = get_server_timestamp().strftime("%Y%m%d")

        if self.special_supply_etc_date <= today:
            result = True
        return result

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
            offer_date=self.offer_date,
            subscription_start_date=self.subscription_start_date,
            subscription_end_date=self.subscription_end_date,
            status=HouseHelper().public_status(
                offer_date=self.offer_date, end_date=self.subscription_end_date,
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
            move_in_year=int(self.move_in_year),
            move_in_month=int(self.move_in_month),
            min_down_payment=self.min_down_payment,
            max_down_payment=self.max_down_payment,
            down_payment_ratio=self.down_payment_ratio,
            reference_url=self.reference_url,
            offer_notice_url=self.offer_notice_url,
            heating_type=self.heating_type,
            vl_rat=self.vl_rat,
            bc_rat=self.bc_rat,
            hhld_total_cnt=self.hhld_total_cnt,
            park_total_cnt=self.park_total_cnt,
            highest_floor=self.highest_floor,
            dong_cnt=self.dong_cnt,
            contract_amount=HouseHelper.convert_contract_amount_to_integer(
                self.contract_amount
            ),
            middle_amount=self.middle_amount,
            remain_amount=self.remain_amount,
            sale_limit=self.sale_limit,
            compulsory_residence=self.compulsory_residence,
            hallway_type=self.hallway_type,
            is_checked=self.is_checked,
            is_available=self.is_available,
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
            move_in_year=int(self.move_in_year),
            move_in_month=int(self.move_in_month),
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

    def to_house_with_public_detail_entity(
        self,
        is_like: bool,
        min_pyoung_number: Optional[float],
        max_pyoung_number: Optional[float],
        min_supply_area: Optional[float],
        max_supply_area: Optional[float],
        avg_supply_price: Optional[float],
        supply_price_per_pyoung: Optional[float],
        min_acquisition_tax: int,
        max_acquisition_tax: int,
        min_supply_price: Optional[int],
        max_supply_price: Optional[int],
        button_links: List[ButtonLinkEntity],
        ticket_usage_results: Optional[TicketUsageResultForHousePublicDetailEntity],
    ) -> HousePublicDetailEntity:
        return HousePublicDetailEntity(
            id=self.real_estate_id,
            name=self.real_estates.name,
            road_address=self.real_estates.road_address,
            jibun_address=self.real_estates.jibun_address,
            si_do=self.real_estates.si_do,
            si_gun_gu=self.real_estates.si_gun_gu,
            dong_myun=self.real_estates.dong_myun,
            ri=self.real_estates.ri,
            road_name=self.real_estates.road_name,
            road_number=self.real_estates.road_number,
            land_number=self.real_estates.land_number,
            latitude=self.real_estates.latitude,
            longitude=self.real_estates.longitude,
            is_available=self.real_estates.is_available,
            is_like=is_like,
            min_pyoung_number=min_pyoung_number,
            max_pyoung_number=max_pyoung_number,
            min_supply_area=min_supply_area,
            max_supply_area=max_supply_area,
            avg_supply_price=avg_supply_price,
            supply_price_per_pyoung=supply_price_per_pyoung,
            min_acquisition_tax=min_acquisition_tax,
            max_acquisition_tax=max_acquisition_tax,
            min_supply_price=min_supply_price,
            max_supply_price=max_supply_price,
            public_sales=self.to_entity(),
            is_special_supply_finished=self.is_special_supply_finished,
            button_links=button_links if button_links else None,
            ticket_usage_results=ticket_usage_results if ticket_usage_results else None,
            report_recently_public_sale_info=self.to_report_entity(),
        )
