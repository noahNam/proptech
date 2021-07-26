from http import HTTPStatus
from typing import Union

import inject
from app.extensions.utils.log_helper import logger_
from core.domains.post.dto.post_dto import GetPostListDto, UpdatePostReadCountDto
from core.domains.post.repository.post_repository import PostRepository
from core.use_case_output import UseCaseSuccessOutput, UseCaseFailureOutput, FailureType

logger = logger_.getLogger(__name__)


class PostBaseUseCase:
    @inject.autoparams()
    def __init__(self, post_repo: PostRepository):
        self._post_repo = post_repo

    def _make_cursor(self, last_post_id: int = None) -> dict:
        return {"cursor": {"last_post_id": last_post_id}}


class GetPostListUseCase(PostBaseUseCase):
    def execute(
        self, dto: GetPostListDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        post_list = self._post_repo.get_post_list_include_article(dto=dto)

        return UseCaseSuccessOutput(
            value=post_list,
            meta=self._make_cursor(
                last_post_id=post_list[-1].id if post_list else None
            ),
        )


class UpdatePostReadCountUseCase(PostBaseUseCase):
    def execute(
        self, dto: UpdatePostReadCountDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        if not dto.user_id:
            return UseCaseFailureOutput(
                type="user_id",
                message=FailureType.NOT_FOUND_ERROR,
                code=HTTPStatus.NOT_FOUND,
            )

        self._post_repo.update_read_count(post_id=dto.post_id)
        return UseCaseSuccessOutput()
