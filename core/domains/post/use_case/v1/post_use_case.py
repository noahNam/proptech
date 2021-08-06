from typing import Union

import inject

from app.extensions.utils.log_helper import logger_
from core.domains.post.dto.post_dto import GetPostListDto, UpdatePostReadCountDto
from core.domains.post.repository.post_repository import PostRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput

logger = logger_.getLogger(__name__)


class PostBaseUseCase:
    @inject.autoparams()
    def __init__(self, post_repo: PostRepository):
        self._post_repo = post_repo


class GetPostListUseCase(PostBaseUseCase):
    def execute(
        self, dto: GetPostListDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        post_list = self._post_repo.get_post_list_include_contents(dto=dto)

        return UseCaseSuccessOutput(value=post_list)


class UpdatePostReadCountUseCase(PostBaseUseCase):
    def execute(
        self, dto: UpdatePostReadCountDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        self._post_repo.update_read_count(post_id=dto.post_id)
        return UseCaseSuccessOutput()
