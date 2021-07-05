from typing import Any

from sqlalchemy import and_, func
from sqlalchemy.orm import scoped_session

from app.extensions.utils.query_helper import RawQueryHelper
from app.persistence.model import RealEstateModel
from core.domains.map.dto.map_dto import CoordinatesRangeDto
from core.domains.map.repository.map_repository import MapRepository

coordinates_range_dto = CoordinatesRangeDto(start_x=127.049,
                                            start_y=37.47,
                                            end_x=127.17,
                                            end_y=37.51,
                                            level=15)
