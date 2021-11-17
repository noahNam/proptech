from http import HTTPStatus
from typing import Union, List

import inject

from app.extensions.utils.log_helper import logger_
from core.domains.post.dto.post_dto import GetPostListDto, UpdatePostReadCountDto
from core.domains.post.entity.post_entity import PostEntity, PostImagePathEntity
from core.domains.post.enum.post_enum import PostCategoryEnum, PostOnlyImageEnum
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
        post_list: List[PostEntity] = self._post_repo.get_post_list_include_contents(
            dto=dto
        )

        path_list = list()
        if dto.only_image == PostOnlyImageEnum.YES.value and post_list:
            for post in post_list:
                if post.post_attachments:
                    for post_attachment in post.post_attachments:
                        path_list.append(PostImagePathEntity(path=post_attachment.path))

            return UseCaseSuccessOutput(
                value=path_list,
                meta=self._make_cursor(
                    last_post_id=post_list[-1].id
                    if post_list and dto.post_category == PostCategoryEnum.NOTICE.value
                    else None
                ),
            )
        return UseCaseSuccessOutput(
            value=post_list,
            meta=self._make_cursor(
                last_post_id=post_list[-1].id
                if post_list and dto.post_category == PostCategoryEnum.NOTICE.value
                else None
            ),
        )


class UpdatePostReadCountUseCase(PostBaseUseCase):
    def execute(
        self, dto: UpdatePostReadCountDto
    ) -> Union[UseCaseSuccessOutput, UseCaseFailureOutput]:
        self._post_repo.update_read_count(post_id=dto.post_id)
        return UseCaseSuccessOutput()
