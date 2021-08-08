from typing import Optional

from pydantic import BaseModel

from core.domains.banner.entity.banner_entity import GetHomeBannerEntity, GetPreSubscriptionBannerEntity


class GetHomeBannerResponseSchema(BaseModel):
    banners: Optional[GetHomeBannerEntity]


class GetPreSubscriptionBannerResponseSchema(BaseModel):
    banners: Optional[GetPreSubscriptionBannerEntity]
