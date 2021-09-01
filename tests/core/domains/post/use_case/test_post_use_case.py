from core.domains.post.dto.post_dto import GetPostListDto, UpdatePostReadCountDto
from core.domains.post.enum.post_enum import PostCategoryEnum, PostCategoryDetailEnum
from core.domains.post.repository.post_repository import PostRepository
from core.domains.post.use_case.v1.post_use_case import (
    GetPostListUseCase,
    UpdatePostReadCountUseCase,
)
from core.use_case_output import UseCaseSuccessOutput


def test_get_post_list_use_case_when_get_notice_list_dto_then_return_post_list(
    session, create_users, post_factory
):
    """
        공지사항 포스트일 경우 Pagination 적용
    """
    post_list = []
    for index in range(25):
        post_list.append(
            post_factory(
                article=True,
                post_attachments=True,
                category_id=PostCategoryEnum.NOTICE.value,
                category_detail_id=PostCategoryDetailEnum.NO_DETAIL.value,
            )
        )

    session.add_all(post_list)
    session.commit()

    dto = GetPostListDto(
        post_category=PostCategoryEnum.NOTICE.value,
        post_category_detail=PostCategoryDetailEnum.NO_DETAIL.value,
        previous_post_id=None,
    )

    result = GetPostListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert len(result.value) == 20
    assert result.meta["cursor"]["last_post_id"] == 6


def test_update_read_count_repo_use_case_when_read_post_then_read_count_plus_one(
    session, post_factory
):
    post = post_factory(
        article=True,
        post_attachments=True,
        category_id=PostCategoryEnum.FAQ.value,
        category_detail_id=PostCategoryDetailEnum.PERSONAL_INFO.value,
    )

    session.add(post)
    session.commit()

    dto = UpdatePostReadCountDto(post_id=post.id)

    result = UpdatePostReadCountUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.type == "success"
