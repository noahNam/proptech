from typing import Union

import inject

from core.domains.banner.dto.banner_dto import GetHomeBannerDto
from core.domains.banner.repository.banner_repository import BannerRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput


class BannerBaseUseCase:
    @inject.autoparams()
    def __init__(self, banner_repo: BannerRepository):
        self._banner_repo = banner_repo


class GetHomeBannerUseCase(BannerBaseUseCase):
    def execute(
            self, dto: GetHomeBannerDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:

        banner_list = self._banner_repo.get_banner_list_include_images(section_type=dto.section_type)





class GetPreSubscriptionBannerUseCase(BannerBaseUseCase):
    pass
