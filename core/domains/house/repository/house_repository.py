from datetime import date

from sqlalchemy import and_, func, or_

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.extensions.utils.time_helper import get_month_from_today, get_server_timestamp
from app.persistence.model import RealEstateModel, PrivateSaleModel, PublicSaleModel, PublicSaleDetailModel, \
    PublicSalePhotoModel
from core.domains.house.dto.house_dto import CoordinatesRangeDto, RealEstateDto

logger = logger_.getLogger(__name__)


class HouseRepository:
    def get_queryset_by_coordinates_range_dto(self, dto: CoordinatesRangeDto):
        query = (
            session.query(RealEstateModel)
                .join(RealEstateModel.private_sales, isouter=True)
                .join(RealEstateModel.public_sales, isouter=True)
                .join(PublicSaleModel.public_sale_details, isouter=True)
                .join(PublicSaleModel.public_sale_photos, isouter=True)
                .filter(or_(and_(RealEstateModel.is_available == "True",
                                 PrivateSaleModel.is_available == "True",
                                 PrivateSaleModel.contract_date >= get_month_from_today(),
                                 PrivateSaleModel.contract_date <= get_server_timestamp()),
                            and_(RealEstateModel.is_available == "True",
                                 PublicSaleModel.is_available == "True"),
                            and_(RealEstateModel.is_available == "True",
                                 PrivateSaleModel.is_available == "True",
                                 PublicSaleModel.is_available == "True",
                                 PrivateSaleModel.contract_date >= get_month_from_today(),
                                 PrivateSaleModel.contract_date <= get_server_timestamp())))
                .filter(func.ST_Contains(func.ST_MakeEnvelope(dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326),
                                         RealEstateModel.coordinates))

        )
        queryset = query.all()
        return queryset

    def make_object_bounding_entity_from_queryset(self, queryset: list):
        if not queryset:
            return None

        # Make Entity
        results = list()
        for query in queryset:
            results.append(query.to_bounding_entity())
        return results
