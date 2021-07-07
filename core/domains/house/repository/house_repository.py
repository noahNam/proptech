from datetime import date

from sqlalchemy import and_, func, or_

from app.extensions.database import session
from app.extensions.utils.time_helper import get_month_from_today
from app.persistence.model import RealEstateModel, PrivateSaleModel, PublicSaleModel, PublicSaleDetailModel, \
    PublicSalePhotoModel
from core.domains.house.dto.house_dto import CoordinatesRangeDto


class MapRepository:
    def get_estates_by_coordinates_range_dto(self, dto: CoordinatesRangeDto):
        query = (
            session.query(RealEstateModel)
                .join(RealEstateModel.private_sales, isouter=True)
                .join(RealEstateModel.public_sales, isouter=True)
                .with_entities(RealEstateModel,
                               func.ST_X(RealEstateModel.coordinates).label("longitude"),
                               func.ST_Y(RealEstateModel.coordinates).label("latitude"),
                               PrivateSaleModel,
                               PublicSaleModel,
                               PublicSaleDetailModel,
                               PublicSalePhotoModel)
                .filter(or_(and_(RealEstateModel.is_available == "True",
                                 PrivateSaleModel.is_available == "True",
                                 PrivateSaleModel.contract_date >= get_month_from_today(),
                                 PrivateSaleModel.contract_date <= date.today()),
                            and_(RealEstateModel.is_available == "True",
                                 PublicSaleModel.is_available == "True"),
                            and_(RealEstateModel.is_available == "True",
                                 PrivateSaleModel.is_available == "True",
                                 PublicSaleModel.is_available == "True",
                                 PrivateSaleModel.contract_date >= get_month_from_today(),
                                 PrivateSaleModel.contract_date <= date.today())))
                .filter(func.ST_Contains(func.ST_MakeEnvelope(dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326),
                                         RealEstateModel.coordinates))
        )
        results = query.all()
