from datetime import datetime
from typing import List

from pydantic import BaseModel

from core.domains.house.entity.house_entity import CalendarInfoEntity


class BannerImageEntity(BaseModel):
    id: int
    banner_id: int
    file_name: str
    path: str
    extension: str
    created_at: datetime
    updated_at: datetime


class BannerEntity(BaseModel):
    id: int
    title: str = None
    desc: str = None
    section_type: int
    sub_topic: int
    reference_url: str = None
    is_active: bool
    is_event: bool
    banner_image: BannerImageEntity = None


class ButtonLinkEntity(BaseModel):
    id: int
    title: str = None
    reference_url: str = None
    section_type: int
    is_active: bool


class GetHomeBannerEntity(BaseModel):
    banner_list: List[BannerEntity] = None
    calendar_infos: List[CalendarInfoEntity] = None


class GetPreSubscriptionBannerEntity(BaseModel):
    banner_list: List[BannerEntity] = None
    button_links: List[ButtonLinkEntity] = None
