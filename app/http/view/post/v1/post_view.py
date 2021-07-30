from flasgger import swag_from
from flask import request

from app.http.requests.v1.post_request import (
    GetPostListRequestSchema,
    UpdatePostReadCountRequestSchema,
)
from app.http.responses.presenters.v1.post_presenter import (
    GetPostListPresenter,
    UpdatePostReadCountPresenter,
)
from app.http.view import auth_required, api, current_user, jwt_required
from core.domains.post.use_case.v1.post_use_case import (
    GetPostListUseCase,
    UpdatePostReadCountUseCase,
)


@api.route("/v1/posts", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_post_list.yml", methods=["GET"])
def get_post_list_view():
    dto = GetPostListRequestSchema(
        post_category=request.args.get("post_category"),
        previous_post_id=request.args.get("previous_post_id"),
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetPostListPresenter().transform(GetPostListUseCase().execute(dto=dto))


@api.route("/v1/posts/<int:post_id>/count", methods=["PATCH"])
@jwt_required
@auth_required
@swag_from("update_post_read_count.yml", methods=["PATCH"])
def update_post_read_count_view(post_id):
    dto = UpdatePostReadCountRequestSchema(
        post_id=post_id, user_id=current_user.id,
    ).validate_request_and_make_dto()

    return UpdatePostReadCountPresenter().transform(
        UpdatePostReadCountUseCase().execute(dto=dto)
    )
