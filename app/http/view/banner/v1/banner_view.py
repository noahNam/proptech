from flask import request

from app.http.requests.v1.banner_request import GetHomeBannerRequestSchema, GetPreSubscriptionBannerRequestSchema
from app.http.responses.presenters.v1.banner_presenter import GetHomeBannerPresenter, GetPreSubscriptionBannerPresenter
from app.http.view import auth_required, api, current_user, jwt_required
from core.domains.banner.use_case.v1.banner_use_case import GetHomeBannerUseCase, GetPreSubscriptionBannerUseCase


@api.route("/v1/banners/home_screen", methods=["GET"])
@jwt_required
@auth_required
def get_home_banner_view():
    dto = GetHomeBannerRequestSchema(
        user_id=current_user.id,
        section_type=request.args.get("section_type")
    ).validate_request_and_make_dto()

    return GetHomeBannerPresenter().transform(
        GetHomeBannerUseCase().execute(dto=dto)
    )


@api.route("/v1/banners/pre_subscription", methods=["GET"])
@jwt_required
@auth_required
def get_pre_subscription_banner_view():
    dto = GetPreSubscriptionBannerRequestSchema(
        section_type=request.args.get("section_type")
    ).validate_request_and_make_dto()

    return GetPreSubscriptionBannerPresenter().transform(
        GetPreSubscriptionBannerUseCase().execute(dto=dto)
    )
