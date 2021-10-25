from typing import Optional

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
from app.extensions.utils.house_helper import HouseHelper
from app.persistence.model.public_sale_model import PublicSaleModel
from core.domains.house.entity.house_entity import (
    PublicSaleDetailEntity,
    PublicSaleDetailReportEntity,
)
from core.domains.house.enum.house_enum import CalcPyoungEnum
from core.domains.report.enum.report_enum import RegionEnum


class PublicSaleDetailModel(db.Model):
    __tablename__ = "public_sale_details"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    public_sales_id = Column(
        BigInteger,
        ForeignKey(PublicSaleModel.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    private_area = Column(Float, nullable=False)
    supply_area = Column(Float, nullable=False)
    supply_price = Column(Integer, nullable=False)
    acquisition_tax = Column(Integer, nullable=False)
    area_type = Column(String(5), nullable=True)
    special_household = Column(SmallInteger, nullable=True)
    multi_children_house_hold = Column(SmallInteger, nullable=True)
    newlywed_house_hold = Column(SmallInteger, nullable=True)
    old_parent_house_hold = Column(SmallInteger, nullable=True)
    first_life_house_hold = Column(SmallInteger, nullable=True)
    general_household = Column(SmallInteger, nullable=True)

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
            private_pyoung_number=HouseHelper.convert_area_to_pyoung(
                self.private_area
            ),  # todo. @Harry 이거 왜 필요한가요?
            supply_area=self.supply_area,
            supply_pyoung_number=HouseHelper.convert_area_to_pyoung(self.supply_area),
            supply_price=self.supply_price,
            total_household=self.total_household,
            acquisition_tax=self.acquisition_tax,
            area_type=self.area_type,
            special_household=self.special_household,
            general_household=self.general_household,
            public_sale_detail_photos=self.public_sale_detail_photos.to_entity()
            if self.public_sale_detail_photos
            else None,
        )

    def to_report_entity(self) -> PublicSaleDetailReportEntity:
        # Sinbad 요청으로 특정 순서로 sort ######################################################################
        sort_dict = {
            RegionEnum.THE_AREA.value: 0,
            RegionEnum.OTHER_GYEONGGI.value: 1,
            RegionEnum.OTHER_REGION.value: 2,
        }
        general_supply_list, special_supply_list = None, None

        if self.general_supply_results:
            general_supply_list = [None for _ in range(len(sort_dict))]

            for general_supply_result in self.general_supply_results:
                index = sort_dict.get(general_supply_result.region)
                general_supply_list[index] = general_supply_result.to_report_entity()

            none_count = general_supply_list.count(None)
            for _ in range(none_count):
                general_supply_list.remove(None)

        if self.special_supply_results:
            special_supply_list = [None for _ in range(len(sort_dict))]

            for special_supply_result in self.special_supply_results:
                index = sort_dict.get(special_supply_result.region)
                special_supply_list[index] = special_supply_result.to_report_entity()

            none_count = special_supply_list.count(None)
            for _ in range(none_count):
                special_supply_list.remove(None)
        ##################################################################################################

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
            pyoung_number=HouseHelper.convert_area_to_pyoung(self.supply_area),
            price_per_meter=int(
                self.supply_price / (self.supply_area / CalcPyoungEnum.CALC_VAR.value)
            )
            if self.supply_price
            else None,
            special_supply_results=special_supply_list
            if self.special_supply_results
            else None,
            general_supply_results=general_supply_list
            if self.general_supply_results
            else None,
        )

    @property
    def total_household(self) -> Optional[int]:
        return self.general_household + self.special_household
