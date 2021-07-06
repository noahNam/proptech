from sqlalchemy import exc

from app.extensions.utils.log_helper import logger_

from app.extensions.database import session
from app.persistence.model import InterestHouseModel
from core.domains.house.dto.house_dto import InterestHouseDto
from core.exceptions import NotUniqueErrorException

logger = logger_.getLogger(__name__)


class HouseRepository:
    def create_interest_house(self, dto: InterestHouseDto) -> None:
        try:
            interest_house = InterestHouseModel(
                user_id=dto.user_id,
                ref_id=dto.ref_id,
                type=dto.type,
                is_like=True
            )

            session.add(interest_house)
            session.commit()
        except exc.IntegrityError as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][create_like_house] ref_id : {dto.ref_id} error : {e}"
            )
            raise NotUniqueErrorException

    def update_interest_house(self, dto: InterestHouseDto) -> None:
        filters = list()
        filters.append(InterestHouseModel.user_id == dto.user_id)
        filters.append(InterestHouseModel.ref_id == dto.ref_id)
        filters.append(InterestHouseModel.type == dto.type)

        try:
            session.query(InterestHouseModel).filter(*filters).update(
                {"is_like": dto.is_like}
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                f"[HouseRepository][update_is_like_house] ref_id : {dto.ref_id} error : {e}"
            )
