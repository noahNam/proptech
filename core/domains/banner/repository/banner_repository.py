from typing import List

from sqlalchemy import and_

from app.extensions.database import session
from app.extensions.utils.log_helper import logger_
from app.persistence.model import BannerModel, ButtonLinkModel
from core.domains.banner.entity.banner_entity import BannerEntity, ButtonLinkEntity

logger = logger_.getLogger(__name__)


class BannerRepository:
    def get_banner_list_include_images(self, section_type: int) -> List[BannerEntity]:
        filters = list()
        filters.append(
            and_(
                BannerModel.section_type == section_type, BannerModel.is_active == True
            )
        )

        query = (
            session.query(BannerModel).join(BannerModel.banner_image).filter(*filters)
        )

        banners = query.all()

        if not banners:
            return []
        return [banner.to_entity() for banner in banners]

    def get_button_link_list(self, section_type: int) -> List[ButtonLinkEntity]:
        filters = list()
        filters.append(
            and_(
                ButtonLinkModel.section_type == section_type,
                ButtonLinkModel.is_active == True,
            )
        )
        query = session.query(ButtonLinkModel).filter(*filters)

        button_links = query.all()

        if not button_links:
            return []
        return [button_link.to_entity() for button_link in button_links]
