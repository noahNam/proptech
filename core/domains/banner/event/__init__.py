from typing import List

from flask import g
from pubsub import pub

from core.domains.banner.entity.banner_entity import BannerEntity, ButtonLinkEntity
from core.domains.banner.enum import BannerTopicEnum
from core.domains.banner.repository.banner_repository import BannerRepository


def get_banner_list(section_type: int) -> None:
    banner_list: List[BannerEntity] = BannerRepository().get_banner_list_include_images(
        section_type=section_type
    )
    setattr(g, BannerTopicEnum.GET_BANNER_LIST, banner_list)


def get_button_link_list(section_type: int) -> None:
    button_link_list: List[ButtonLinkEntity] = BannerRepository().get_button_link_list(
        section_type=section_type
    )
    setattr(g, BannerTopicEnum.GET_BUTTON_LINK_LIST, button_link_list)


pub.subscribe(get_banner_list, BannerTopicEnum.GET_BANNER_LIST)
pub.subscribe(get_button_link_list, BannerTopicEnum.GET_BUTTON_LINK_LIST)
