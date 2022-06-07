from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DateTime,
    String,
    SmallInteger,
    Boolean,
    func, Numeric
)
from sqlalchemy.orm import relationship

from app import db
from core.domains.house.entity.house_entity import PrivateSaleEntity


class PrivateSaleModel(db.Model):
    __tablename__ = "private_sales"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    real_estate_id = Column(
        BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True,
    )
    name = Column(String(50), nullable=True)
    building_type = Column(String(5), nullable=True)
    build_year = Column(String(4), nullable=True)
    move_in_date = Column(String(8), nullable=True)
    dong_cnt = Column(SmallInteger, nullable=True)
    hhld_cnt = Column(SmallInteger, nullable=True)
    heat_type = Column(String(6), nullable=True)
    hallway_type = Column(String(4), nullable=True)
    builder = Column(String(64), nullable=True)
    park_total_cnt = Column(SmallInteger, nullable=True)
    park_ground_cnt = Column(SmallInteger, nullable=True)
    park_underground_cnt = Column(SmallInteger, nullable=True)
    cctv_cnt = Column(SmallInteger, nullable=True)
    welfare = Column(String(200), nullable=True)
    bc_rat = Column(Numeric(6, 2), nullable=True)
    vl_rat = Column(Numeric(6, 2), nullable=True)
    summer_mgmt_cost = Column(SmallInteger, nullable=True)
    winter_mgmt_cost = Column(SmallInteger, nullable=True)
    avg_mgmt_cost = Column(SmallInteger, nullable=True)
    public_ref_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=True)
    rebuild_ref_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=True)
    trade_status = Column(SmallInteger, nullable=False, default=0)
    deposit_status = Column(SmallInteger, nullable=False, default=0)
    is_available = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # relationship
    private_sale_details = relationship(
        "PrivateSaleDetailModel", backref="private_sales", uselist=True, primaryjoin="PrivateSaleModel.id == foreign(PrivateSaleDetailModel.private_sale_id)"
    )
    dong_infos = relationship("DongInfoModel", backref="private_sales", uselist=True, primaryjoin="PrivateSaleModel.id == foreign(DongInfoModel.private_sale_id)")
    house_photos = relationship(
        "HousePhotoModel", backref="private_sales", uselist=True, primaryjoin="PrivateSaleModel.id == foreign(HousePhotoModel.private_sale_id)",
    )
    house_type_photos = relationship(
        "HouseTypePhotoModel", backref="private_sales", uselist=True, primaryjoin="PrivateSaleModel.id == foreign(HouseTypePhotoModel.private_sale_id)",
    )
    private_sale_avg_prices = relationship(
        "PrivateSaleAvgPriceModel",
        backref="private_sale_avg_prices",
        uselist=True,
        primaryjoin="PrivateSaleModel.id == foreign(PrivateSaleAvgPriceModel.private_sale_id)",
    )

    def to_entity(self) -> PrivateSaleEntity:
        return PrivateSaleEntity(
            id=self.id,
            real_estate_id=self.real_estate_id,
            name=self.name,
            building_type=self.building_type,
            build_year=self.build_year,
            move_in_date=self.move_in_date,
            dong_cnt=self.dong_cnt,
            hhld_cnt=self.hhld_cnt,
            heat_type=self.heat_type,
            hallway_type=self.heat_hallway_typetype,
            builder=self.builder,
            park_total_cnt=self.park_total_cnt,
            park_ground_cnt=self.park_ground_cnt,
            park_underground_cnt=self.park_underground_cnt,
            cctv_cnt=self.cctv_cnt,
            welfare=self.welfare,
            bc_rat=self.bc_rat,
            vl_rat=self.vl_rat,
            summer_mgmt_cost=self.summer_mgmt_cost,
            winter_mgmt_cost=self.winter_mgmt_cost,
            avg_mgmt_cost=self.avg_mgmt_cost,
            public_ref_id=self.public_ref_id,
            rebuild_ref_id=self.rebuild_ref_id,
            trade_status=self.trade_status,
            deposit_status=self.deposit_status,
            is_available=self.is_available,
            created_at=self.created_at,
            updated_at=self.updated_at,
            private_sale_details=[
                private_sale_detail.to_entity()
                for private_sale_detail in self.private_sale_details
            ]
            if self.private_sale_details
            else None,
            dong_infos=[
                dong_info.to_entity()
                for dong_info in self.dong_infos
            ]
            if self.dong_infos
            else None,
            house_photos=[
                house_photo.to_entity()
                for house_photo in self.house_photos
            ]
            if self.house_photos
            else None,
            house_type_photos=[
                house_type_photo.to_entity()
                for house_type_photo in self.house_type_photos
            ]
            if self.house_type_photos
            else None,
            private_sale_avg_prices=[
                private_sale_avg_price.to_entity()
                for private_sale_avg_price in self.private_sale_avg_prices
            ]
            if self.private_sale_avg_prices
            else None,
        )
