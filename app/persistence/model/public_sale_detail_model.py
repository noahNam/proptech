from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    ForeignKey,
    Float,
    String,
    SmallInteger,
)
from sqlalchemy.orm import relationship, backref

from app import db
from app.persistence.model.public_sale_model import PublicSaleModel
from core.domains.house.entity.house_entity import (
    PublicSaleDetailEntity,
    PublicSaleDetailReportEntity,
)
from core.domains.house.enum.house_enum import PricePerMeterEnum


class PublicSaleDetailModel(db.Model):
    __tablename__ = "public_sale_details"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    public_sales_id = Column(
        BigInteger, ForeignKey(PublicSaleModel.id, ondelete="CASCADE"), nullable=False
    )
    private_area = Column(Float, nullable=False)
    supply_area = Column(Float, nullable=False)
    supply_price = Column(Integer, nullable=False)
    acquisition_tax = Column(Integer, nullable=False)
    area_type = Column(String(5), nullable=True)
    special_household = Column(SmallInteger, nullable=False)
    multi_children_house_hold = Column(SmallInteger, nullable=False)
    newlywed_house_hold = Column(SmallInteger, nullable=False)
    old_parent_house_hold = Column(SmallInteger, nullable=False)
    first_life_house_hold = Column(SmallInteger, nullable=False)
    general_household = Column(SmallInteger, nullable=False)

    # 1:1 relationship
    public_sale_detail_photos = relationship(
        "PublicSaleDetailPhotoModel",
        backref=backref("public_sale_details"),
        uselist=False,
    )

    special_supply_results = relationship(
        "SpecialSupplyResultModel", backref=backref("public_sale_details"),
    )

    general_supply_results = relationship(
        "GeneralSupplyResultModel", backref=backref("public_sale_details"),
    )

    def to_entity(self) -> PublicSaleDetailEntity:
        return PublicSaleDetailEntity(
            id=self.id,
            public_sales_id=self.public_sales_id,
            private_area=self.private_area,
            supply_area=self.supply_area,
            supply_price=self.supply_price,
            acquisition_tax=self.acquisition_tax,
            area_type=self.area_type,
            public_sale_detail_photos=self.public_sale_detail_photos.to_entity()
            if self.public_sale_detail_photos
            else None,
            special_household=self.special_household,
            general_household=self.general_household,
        )

    def to_report_entity(self) -> PublicSaleDetailReportEntity:
        return PublicSaleDetailReportEntity(
            id=self.id,
            public_sales_id=self.public_sales_id,
            private_area=self.private_area,
            supply_area=self.supply_area,
            supply_price=self.supply_price,
            acquisition_tax=self.acquisition_tax,
            area_type=self.area_type,
            public_sale_detail_photos=self.public_sale_detail_photos.to_entity()
            if self.public_sale_detail_photos
            else None,
            special_household=self.special_household,
            multi_children_house_hold=self.multi_children_house_hold,
            newlywed_house_hold=self.newlywed_house_hold,
            old_parent_house_hold=self.old_parent_house_hold,
            first_life_house_hold=self.first_life_house_hold,
            general_household=self.general_household,
            pyoung_number=round(self.supply_area / PricePerMeterEnum.CALC_VAR.value)
            if self.supply_area
            else None,
            price_per_meter=int(
                self.supply_price
                / (self.supply_area / PricePerMeterEnum.CALC_VAR.value)
            )
            if self.supply_price
            else None,
            special_supply_results=[
                special_supply_result.to_report_entity()
                for special_supply_result in self.special_supply_results
            ]
            if self.special_supply_results
            else None,
            general_supply_results=[
                general_supply_result.to_report_entity()
                for general_supply_result in self.general_supply_results
            ]
            if self.general_supply_results
            else None,
        )
