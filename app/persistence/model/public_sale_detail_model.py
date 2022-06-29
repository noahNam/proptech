from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    SmallInteger,
    Numeric,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship

from app import db
from app.extensions.utils.house_helper import HouseHelper
from app.extensions.utils.image_helper import S3Helper
from core.domains.house.entity.house_entity import (
    PublicSaleDetailEntity,
    PublicSaleDetailReportEntity,
)
from core.domains.house.enum.house_enum import CalcPyoungEnum
from core.domains.report.enum.report_enum import RegionEnum


class PublicSaleDetailModel(db.Model):
    __tablename__ = "public_sale_details"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    public_sale_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )
    area_type = Column(String(5), nullable=True)
    private_area = Column(Numeric(6, 2), nullable=False)
    supply_area = Column(Numeric(6, 2), nullable=False)
    supply_price = Column(Integer, nullable=False)
    acquisition_tax = Column(Integer, nullable=False)
    special_household = Column(SmallInteger, nullable=True)
    multi_children_household = Column(SmallInteger, nullable=True)
    newlywed_household = Column(SmallInteger, nullable=True)
    old_parent_household = Column(SmallInteger, nullable=True)
    first_life_household = Column(SmallInteger, nullable=True)
    general_household = Column(SmallInteger, nullable=True)
    bay = Column(SmallInteger, nullable=True)
    pansang_tower = Column(String(10), nullable=True)
    kitchen_window = Column(String(1), nullable=True)
    direct_window = Column(String(1), nullable=True)
    alpha_room = Column(String(1), nullable=True)
    cyber_model_house_link = Column(String(200), nullable=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # relationship
    public_sale_detail_photos = relationship(
        "PublicSaleDetailPhotoModel",
        backref="public_sale_details",
        uselist=False,
        primaryjoin="PublicSaleDetailModel.id == foreign(PublicSaleDetailPhotoModel.public_sale_detail_id)",
    )

    special_supply_results = relationship(
        "SpecialSupplyResultModel",
        backref="public_sale_details",
        uselist=True,
        primaryjoin="PublicSaleDetailModel.id == foreign(SpecialSupplyResultModel.public_sale_detail_id)",
    )

    general_supply_results = relationship(
        "GeneralSupplyResultModel",
        backref="public_sale_details",
        uselist=True,
        primaryjoin="PublicSaleDetailModel.id == foreign(GeneralSupplyResultModel.public_sale_detail_id)",
    )

    def to_entity(self) -> PublicSaleDetailEntity:
        return PublicSaleDetailEntity(
            id=self.id,
            public_sale_id=self.public_sale_id,
            private_area=self.private_area,
            private_pyoung_number=HouseHelper.convert_area_to_pyoung(
                self.private_area
            ),  # Sinbad 요청 entity
            supply_area=self.supply_area,
            supply_pyoung_number=HouseHelper.convert_area_to_pyoung(
                self.supply_area
            ),  # Sinbad 요청 entity
            supply_price=self.supply_price,
            total_household=self.total_household,
            acquisition_tax=self.acquisition_tax,
            area_type=self.area_type,
            special_household=self.special_household,
            general_household=self.general_household,
            public_sale_detail_photos=S3Helper.get_cloudfront_url()
            + "/"
            + self.public_sale_detail_photos.path
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
            public_sale_id=self.public_sale_id,
            private_area=self.private_area,
            supply_area=self.supply_area,
            supply_price=self.supply_price,
            acquisition_tax=self.acquisition_tax,
            area_type=self.area_type,
            public_sale_detail_photo=S3Helper.get_cloudfront_url()
            + "/"
            + self.public_sale_detail_photos.path
            if self.public_sale_detail_photos
            else None,
            special_household=self.special_household,
            multi_children_household=self.multi_children_household,
            newlywed_household=self.newlywed_household,
            old_parent_household=self.old_parent_household,
            first_life_household=self.first_life_household,
            general_household=self.general_household,
            total_household=self.total_household,
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
    def total_household(self) -> int:
        general_household = self.general_household if self.general_household else 0
        special_household = self.special_household if self.special_household else 0
        return general_household + special_household
