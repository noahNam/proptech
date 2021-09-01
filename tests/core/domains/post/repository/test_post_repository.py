from core.domains.post.dto.post_dto import GetPostListDto
from core.domains.post.enum.post_enum import PostCategoryEnum, PostCategoryDetailEnum
from core.domains.post.repository.post_repository import PostRepository


def test_get_post_list_repo_then_return_post_list(session, post_factory):
    post1 = post_factory(
        article=True,
        post_attachments=True,
        category_id=PostCategoryEnum.NOTICE.value,
        category_detail_id=PostCategoryDetailEnum.NO_DETAIL.value,
    )
    post2 = post_factory(
        article=True,
        post_attachments=True,
        category_id=PostCategoryEnum.NOTICE.value,
        category_detail_id=PostCategoryDetailEnum.SUBSCRIPTION_CREDENTIAL.value,
    )

    post3 = post_factory(
        article=True,
        post_attachments=True,
        category_id=PostCategoryEnum.NOTICE.value,
        category_detail_id=PostCategoryDetailEnum.NO_DETAIL.value,
    )
    post4 = post_factory(
        article=True,
        post_attachments=True,
        category_id=PostCategoryEnum.FAQ.value,
        category_detail_id=PostCategoryDetailEnum.PERSONAL_INFO.value,
    )

    session.add_all([post1, post2, post3, post4])
    session.commit()

    get_post_list_dto = GetPostListDto(
        post_category=PostCategoryEnum.NOTICE.value,
        post_category_detail=PostCategoryDetailEnum.NO_DETAIL.value,
    )

    post_list_notice = PostRepository().get_post_list_include_contents(
        dto=get_post_list_dto
    )

    get_post_list_dto.post_category = PostCategoryEnum.FAQ.value
    get_post_list_dto.post_category_detail = PostCategoryDetailEnum.PERSONAL_INFO.value
    post_list_faq = PostRepository().get_post_list_include_contents(
        dto=get_post_list_dto
    )

    assert len(post_list_notice) == 2
    assert len(post_list_faq) == 1


def test_update_read_count_repo_when_read_post_then_read_count_plus_one(
        session, create_users, post_factory
):
    post = post_factory(
        article=True,
        post_attachments=True,
        category_id=PostCategoryEnum.NOTICE.value,
        category_detail_id=PostCategoryDetailEnum.NO_DETAIL.value,
    )

    session.add(post)
    session.commit()

    PostRepository().update_read_count(post_id=post.id)

    dto = GetPostListDto(
        post_category=PostCategoryEnum.NOTICE.value,
        post_category_detail=PostCategoryDetailEnum.NO_DETAIL.value,
    )
    post_list = PostRepository().get_post_list_include_contents(dto=dto)

    assert post_list[0].read_count == 1


def test_get_post_list_repo_when_load_more_notice_post_then_return_post_list(
        session, create_users, post_factory
):
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

    get_post_list_dto = GetPostListDto(
        post_category=PostCategoryEnum.NOTICE.value,
        post_category_detail=PostCategoryDetailEnum.NO_DETAIL.value,
        previous_post_id=None
    )

    post_result_1 = PostRepository().get_post_list_include_contents(
        dto=get_post_list_dto
    )

    get_post_list_dto2 = GetPostListDto(
        post_category=PostCategoryEnum.NOTICE.value,
        post_category_detail=PostCategoryDetailEnum.NO_DETAIL.value,
        previous_post_id=6
    )

    post_result_2 = PostRepository().get_post_list_include_contents(
        dto=get_post_list_dto2
    )

    assert len(post_result_1) == 20
    assert len(post_result_2) == 5
