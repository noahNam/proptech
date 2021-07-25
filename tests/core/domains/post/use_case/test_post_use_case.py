from core.domains.post.dto.post_dto import GetPostListDto, UpdatePostReadCountDto
from core.domains.post.enum.post_enum import PostCategoryEnum
from core.domains.post.use_case.v1.post_use_case import (
    GetPostListUseCase,
    UpdatePostReadCountUseCase,
)
from core.use_case_output import UseCaseSuccessOutput


def test_get_post_list_use_case_when_load_more_post_then_return_post_list(
    session, create_users, post_factory
):
    post_list = []
    for index in range(15):
        post_list.append(
            post_factory(
                Article=True,
                user_id=create_users[0].id,
                category_id=PostCategoryEnum.NOTICE.value,
            )
        )

    session.add_all(post_list)
    session.commit()

    dto = GetPostListDto(
        user_id=create_users[0].id,
        post_category=PostCategoryEnum.NOTICE.value,
        previous_post_id=None,
    )

    result = GetPostListUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert len(result.value) == 10
    assert result.meta["cursor"]["last_post_id"] == 6


def test_update_read_count_repo_use_case_when_read_post_then_read_count_plus_one(
    session, create_users, post_factory
):
    post = post_factory(
        Article=True,
        user_id=create_users[0].id,
        category_id=PostCategoryEnum.NOTICE.value,
    )

    session.add(post)
    session.commit()

    dto = UpdatePostReadCountDto(user_id=create_users[0].id, post_id=post.id)

    result = UpdatePostReadCountUseCase().execute(dto=dto)

    assert isinstance(result, UseCaseSuccessOutput)
    assert result.type == "success"
