import json
from flask import url_for

from core.domains.post.enum.post_enum import PostCategoryEnum


def test_get_post_list_include_article_view_when_watch_notice_and_faq_then_return_teb_posts(
        client, session, test_request_context, make_header, make_authorization, create_users, post_factory
):
    post_list = []
    for index in range(15):
        post_list.append(post_factory(
            Article=True,
            user_id=create_users[0].id,
            category_id=PostCategoryEnum.NOTICE.value
        ))

    session.add_all(post_list)
    session.commit()

    user_id = create_users[0].id
    authorization = make_authorization(user_id=user_id)
    headers = make_header(
        authorization=authorization,
        content_type="application/json",
        accept="application/json",
    )

    # 첫 페이징
    dict_ = dict(post_category=PostCategoryEnum.NOTICE.value, previous_post_id=None)
    with test_request_context:
        response1 = client.get(
            url_for("api/tanos.get_post_list_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response1.get_json()["data"]
    meta = response1.get_json()["meta"]
    assert response1.status_code == 200
    assert len(data["posts"]) == 10
    assert meta["cursor"]["last_post_id"] == 6

    # 두번째 페이징
    dict_ = dict(post_category=PostCategoryEnum.NOTICE.value, previous_post_id=6)
    with test_request_context:
        response2 = client.get(
            url_for("api/tanos.get_post_list_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response2.get_json()["data"]
    meta = response2.get_json()["meta"]
    assert response2.status_code == 200
    assert len(data["posts"]) == 5
    assert meta["cursor"]["last_post_id"] == 1


def test_update_post_read_count_view_when_watch_notice_and_faq_then_return_success(
        client, session, test_request_context, make_header, make_authorization, create_users, post_factory
):
    post = post_factory(
        Article=True,
        user_id=create_users[0].id,
        category_id=PostCategoryEnum.NOTICE.value
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

    dict_ = dict(post_category=PostCategoryEnum.NOTICE.value, previous_post_id=None)
    with test_request_context:
        response = client.get(
            url_for("api/tanos.get_post_list_view"),
            data=json.dumps(dict_),
            headers=headers,
        )

    data = response.get_json()["data"]
    meta = response.get_json()["meta"]
    assert response.status_code == 200
    assert data["posts"][0]['read_count'] == 1
    assert meta["cursor"]["last_post_id"] == 1
