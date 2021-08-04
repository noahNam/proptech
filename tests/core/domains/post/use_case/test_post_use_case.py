from core.domains.post.dto.post_dto import GetPostListDto, UpdatePostReadCountDto
from core.domains.post.enum.post_enum import PostCategoryEnum, PostCategoryDetailEnum
from core.domains.post.use_case.v1.post_use_case import (
    GetPostListUseCase,
    UpdatePostReadCountUseCase,
)
from core.use_case_output import UseCaseSuccessOutput


def test_get_post_list_use_case_when_get_post_list_dto_then_return_post_list(
    session, post_factory
):
    post_list = []
    for index in range(15):
        post_list.append(
            post_factory(
                article=True,
                post_attachments=True,
                category_id=PostCategoryEnum.FAQ.value,
                category_detail_id=PostCategoryDetailEnum.ACCOUNT_AUTH.value,
            )
        )

    session.add_all(post_list)
    session.commit()

    dto = GetPostListDto(
        post_category=PostCategoryEnum.FAQ.value,
        post_category_detail=PostCategoryDetailEnum.ACCOUNT_AUTH.value,
    )

    result = GetPostListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert len(result.value) == 15


def test_update_read_count_repo_use_case_when_read_post_then_read_count_plus_one(
    session, post_factory
):
    post = post_factory(
        article=True,
        post_attachments=True,
        category_id=PostCategoryEnum.FAQ.value,
        category_detail_id=PostCategoryDetailEnum.ACCOUNT_AUTH.value,
    )

    session.add(post)
    session.commit()

    dto = UpdatePostReadCountDto(post_id=post.id)

    result = UpdatePostReadCountUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.type == "success"
