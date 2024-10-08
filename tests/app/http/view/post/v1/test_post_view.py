import json

import pytest
from flask import url_for

from core.domains.post.enum.post_enum import PostCategoryEnum, PostCategoryDetailEnum


def test_get_post_list_include_contents_view_when_watch_notice_then_return_pagination_post_lists(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    post_factory,
):
    """
        공지사항 포스트일 경우 Pagination 처리된 리스트 반환
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

    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response_1 = client.get(
            url_for(
                "api/tanos.get_post_list_view",
                post_category=PostCategoryEnum.NOTICE.value,
                post_category_detail=PostCategoryDetailEnum.NO_DETAIL.value,
                previous_post_id=None,
            ),
            headers=headers,
        )

    data = response_1.get_json()["data"]
    meta = response_1.get_json()["meta"]
    assert response_1.status_code == 200
    assert len(data["posts"]) == 20
    assert meta["cursor"]["last_post_id"] == 6

    with test_request_context:
        response_2 = client.get(
            url_for(
                "api/tanos.get_post_list_view",
                post_category=PostCategoryEnum.NOTICE.value,
                post_category_detail=PostCategoryDetailEnum.NO_DETAIL.value,
                previous_post_id=6,
            ),
            headers=headers,
        )

    data = response_2.get_json()["data"]
    meta = response_2.get_json()["meta"]
    assert response_2.status_code == 200
    assert len(data["posts"]) == 5
    assert meta["cursor"]["last_post_id"] == 1


def test_update_post_read_count_view_when_watch_notice_and_faq_then_return_success(
    client,
    session,
    test_request_context,
    make_header,
    make_authorization,
    create_users,
    post_factory,
):
    post = post_factory(
        article=True,
        post_attachments=True,
        category_id=PostCategoryEnum.NOTICE.value,
        category_detail_id=PostCategoryDetailEnum.NO_DETAIL.value,
    )

    session.add(post)
    session.commit()

    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    with test_request_context:
        response = client.patch(
            url_for("api/tanos.update_post_read_count_view", post_id=post.id),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["result"] == "success"

    with test_request_context:
        response = client.get(
            url_for(
                "api/tanos.get_post_list_view",
                post_category=PostCategoryEnum.NOTICE.value,
                post_category_detail=PostCategoryDetailEnum.NO_DETAIL.value,
            ),
            headers=headers,
        )

    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["posts"][0]["read_count"] == 1
