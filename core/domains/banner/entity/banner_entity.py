from datetime import datetime

from pydantic import BaseModel


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
