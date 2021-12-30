from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, backref, column_property

from app import db
from core.domains.house.entity.house_entity import (
    DetailCalendarInfoEntity,
    SimpleCalendarInfoEntity,
    RealEstateReportEntity,
    RealEstateLegalCodeEntity,
    AddSupplyAreaEntity,
)


class RealEstateModel(db.Model):
    __tablename__ = "real_estates"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, nullable=False,
    )
    name = Column(String(50), nullable=True)
    road_address = Column(String(100), nullable=False)
    jibun_address = Column(String(100), nullable=False)
    si_do = Column(String(20), nullable=False)
    si_gun_gu = Column(String(16), nullable=False)
    dong_myun = Column(String(16), nullable=False)
    ri = Column(String(12), nullable=True)
    road_name = Column(String(30), nullable=True)
    road_number = Column(String(10), nullable=True)
    land_number = Column(String(10), nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    front_legal_code = Column(String(5), nullable=False, unique=False, index=True)
    back_legal_code = Column(String(5), nullable=False, unique=False, index=True)
    coordinates = Column(
        Geometry(geometry_type="POINT", srid=4326).with_variant(String, "sqlite"),
        nullable=True,
    )

    jibun_address_ts = Column(
        TSVECTOR().with_variant(String(100), "sqlite"), nullable=True
    )
    road_address_ts = Column(
        TSVECTOR().with_variant(String(100), "sqlite"), nullable=True
    )

    latitude = column_property(coordinates.ST_Y())
    longitude = column_property(coordinates.ST_X())

    private_sales = relationship(
        "PrivateSaleModel", backref=backref("real_estates"), uselist=False,
    )
    public_sales = relationship(
        "PublicSaleModel", backref=backref("real_estates"), uselist=False,
    )

    def to_detail_calendar_info_entity(self, is_like: bool) -> DetailCalendarInfoEntity:
        return DetailCalendarInfoEntity(
            is_like=is_like,
            id=self.id,
            name=self.name,
            road_address=self.road_address,
            jibun_address=self.calender_address,
            public_sale=self.public_sales.to_calendar_entity()
            if self.public_sales
            else None,
        )

    def to_simple_calendar_info_entity(self, is_like: bool) -> SimpleCalendarInfoEntity:
        return SimpleCalendarInfoEntity(
            is_like=is_like,
            id=self.id,
            name=self.name,
            road_address=self.road_address,
            jibun_address=self.calender_address,
            public_sale=self.public_sales.to_calendar_entity()
            if self.public_sales
            else None,
        )

    def to_report_entity(self) -> RealEstateReportEntity:
        return RealEstateReportEntity(
            id=self.id,
            jibun_address=self.jibun_address,
            si_do=self.si_do,
            si_gun_gu=self.si_gun_gu,
            latitude=self.latitude,
            longitude=self.longitude,
        )

    def to_legal_code_entity(self) -> RealEstateLegalCodeEntity:
        return RealEstateLegalCodeEntity(
            id=self.id,
            jibun_address=self.jibun_address,
            si_do=self.si_do,
            si_gun_gu=self.si_gun_gu,
            dong_myun=self.dong_myun,
        )

    @property
    def calender_address(self) -> Optional[str]:
        if not self.si_do:
            return ""
        elif self.si_do == "세종특별자치시":
            # 세종시는 시군구가 무조건 없음
            return f"{self.si_do} {self.dong_myun} {self.land_number}"
        else:
            return (
                f"{self.si_do} {self.si_gun_gu} {self.dong_myun} {self.land_number}"
                if self.dong_myun != ""
                else f"{self.si_do} {self.si_gun_gu}"
            )

    # todo. AddSupplyAreaUseCase에서 사용 -> antman 이관 후 삭제 필요
    def to_add_supply_area_entity(self) -> Optional[AddSupplyAreaEntity]:
        return AddSupplyAreaEntity(
            req_front_legal_code=self.req_front_legal_code,
            req_back_legal_code=self.req_back_legal_code,
            req_land_number=self.req_land_number,
            req_real_estate_id=self.req_real_estate_id,
            req_real_estate_name=self.req_real_estate_name,
            req_private_sales_id=self.req_private_sales_id,
            req_private_sale_name=self.req_private_sale_name,
            req_jibun_address=self.req_jibun_address,
            req_road_address=self.req_road_address,
            resp_rnum=self.resp_rnum,
            resp_total_count=self.resp_total_count,
            resp_name=self.resp_name,
            resp_dong_nm=self.resp_dong_nm,
            resp_ho_nm=self.resp_ho_nm,
            resp_flr_no_nm=self.resp_flr_no_nm,
            resp_area=self.resp_area,
            resp_jibun_address=self.resp_jibun_address,
            resp_road_address=self.resp_road_address,
            resp_expos_pubuse_gb_cd_nm=self.resp_expos_pubuse_gb_cd_nm,
            resp_main_atch_gb_cd=self.resp_main_atch_gb_cd,
            resp_main_atch_gb_cd_nm=self.resp_main_atch_gb_cd_nm,
            resp_main_purps_cd=self.resp_main_purps_cd,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
