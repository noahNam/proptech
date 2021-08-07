import inject

from core.domains.banner.repository.banner_repository import BannerRepository


class BannerBaseUseCase:
    @inject.autoparams()
    def __init__(self, banner_repo: BannerRepository):
        self._banner_repo = banner_repo


class GetHomeBannerUseCase(BannerBaseUseCase):
    pass


class GetPreSubscriptionBannerUseCase(BannerBaseUseCase):
    pass
