from core.domains.post.dto.post_dto import GetPostListDto
from core.domains.post.enum.post_enum import PostCategoryEnum
from core.domains.post.repository.post_repository import PostRepository

get_post_list_dto = GetPostListDto(
    post_category=PostCategoryEnum.NOTICE.value,
    previous_post_id=None
)


def test_get_post_list_then_return_post_list(session, create_users, post_factory):
    post1 = post_factory(
        Article=True,
        user_id=create_users[0].id,
        category_id=PostCategoryEnum.NOTICE.value
    )
    post2 = post_factory(
        Article=True,
        user_id=create_users[0].id,
        category_id=PostCategoryEnum.NOTICE.value
    )

    post3 = post_factory(
        Article=True,
        user_id=create_users[1].id,
        category_id=PostCategoryEnum.NOTICE.value
    )
    post4 = post_factory(
        Article=True,
        user_id=create_users[2].id,
        category_id=PostCategoryEnum.FAQ.value
    )

    session.add_all([post1, post2, post3, post4])
    session.commit()

    post_list_notice = PostRepository().get_post_list_include_article(
        dto=get_post_list_dto
    )

    get_post_list_dto.post_category = PostCategoryEnum.FAQ.value
    post_list_faq = PostRepository().get_post_list_include_article(
        dto=get_post_list_dto
    )

    assert len(post_list_notice) == 3
    assert len(post_list_faq) == 1


def test_get_post_list_when_load_more_post_then_return_post_list(session, create_users, post_factory):
    post_list = []
    for index in range(15):
        post_list.append(post_factory(
            Article=True,
            user_id=create_users[0].id,
            category_id=PostCategoryEnum.NOTICE.value
        ))

    session.add_all(post_list)
    session.commit()

    post_result_1 = PostRepository().get_post_list_include_article(
        dto=get_post_list_dto
    )

    get_post_list_dto2 = GetPostListDto(
        post_category=PostCategoryEnum.NOTICE.value,
        previous_post_id=6
    )

    post_result_2 = PostRepository().get_post_list_include_article(
        dto=get_post_list_dto2
    )

    assert len(post_result_1) == 10
    assert len(post_result_2) == 5


def test_update_read_count_when_read_post_then_read_count_puls_one(session, create_users, post_factory):
    post = post_factory(
        Article=True,
        user_id=create_users[0].id,
        category_id=PostCategoryEnum.NOTICE.value
    )

    session.add(post)
    session.commit()

    PostRepository().update_read_count(post_id=post.id)

    dto = GetPostListDto(
        post_category=PostCategoryEnum.NOTICE.value,
        previous_post_id=None
    )
    post_list = PostRepository().get_post_list_include_article(
        dto=dto
    )

    assert post_list[0].read_count == 1
