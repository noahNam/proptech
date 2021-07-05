from sqlalchemy import and_, func

from app.extensions.database import session
from app.persistence.model import RealEstateModel, RealTradeModel, PreSaleModel
from core.domains.map.dto.map_dto import CoordinatesRangeDto


class MapRepository:
    def get_estates_by_coordinates_range_dto(self, dto: CoordinatesRangeDto):
        return session.query(RealEstateModel, RealTradeModel, PreSaleModel,
                             func.ST_X(RealEstateModel.coordinates).label("longitude"),
                             func.ST_Y(RealEstateModel.coordinates).label("latitude")) \
            .join(RealTradeModel, RealTradeModel.real_estate_id == RealEstateModel.id, isouter=True) \
            .join(PreSaleModel, PreSaleModel.real_estate_id == RealEstateModel.id, isouter=True) \
            .filter(RealEstateModel.is_available == "True") \
            .filter(func.ST_Contains(func.ST_MakeEnvelope(dto.start_x, dto.end_y, dto.end_x, dto.start_y, 4326),
                                     RealEstateModel.coordinates))
