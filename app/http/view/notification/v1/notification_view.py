from flasgger import swag_from
from flask import request
from flask_jwt_extended import jwt_required

from app.http.requests.v1.notification_request import (
    GetNotificationRequestSchema,
    GetBadgeRequestSchema,
    UpdateNotificationRequestSchema,
    GetReceiveNotificationSettingRequestSchema,
    UpdateReceiveNotificationSettingRequestSchema,
)
from app.http.responses.presenters.v1.notification_presenter import (
    GetNotificationPresenter,
    GetBadgePresenter,
    UpdateNotificationPresenter,
    GetReceiveNotificationSettingPresenter,
    UpdateReceiveNotificationSettingPresenter,
)
from app.http.view import auth_required, api, current_user
from core.domains.notification.use_case.v1.notification_use_case import (
    GetNotificationUseCase,
    GetBadgeUseCase,
    UpdateNotificationUseCase,
    GetReceiveNotificationSettingUseCase,
    UpdateReceiveNotificationSettingUseCase,
)


@api.route("/v1/notifications", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_notification.yml", methods=["GET"])
def get_notification_view():
    dto = GetNotificationRequestSchema(
        category=request.args.get("category"), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetNotificationPresenter().transform(
        GetNotificationUseCase().execute(dto=dto)
    )


@api.route("/v1/notifications/badge", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_badge.yml", methods=["GET"])
def get_badge_view():
    dto = GetBadgeRequestSchema(
        badge_type=request.args.get("badge_type"), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return GetBadgePresenter().transform(GetBadgeUseCase().execute(dto=dto))


@api.route("/v1/notifications/<int:notification_id>", methods=["PATCH"])
@jwt_required
@auth_required
@swag_from("update_notification.yml", methods=["PATCH"])
def update_notification_view(notification_id):
    dto = UpdateNotificationRequestSchema(
        notification_id=notification_id, user_id=current_user.id,
    ).validate_request_and_make_dto()

    return UpdateNotificationPresenter().transform(
        UpdateNotificationUseCase().execute(dto=dto)
    )


@api.route("/v1/notifications/receive", methods=["GET"])
@jwt_required
@auth_required
@swag_from("get_receive_notification_settings.yml", methods=["GET"])
def get_receive_notification_settings_view():
    GetReceiveNotificationSettingRequestSchema(
        user_id=current_user.id,
    ).validate_request()

    return GetReceiveNotificationSettingPresenter().transform(
        GetReceiveNotificationSettingUseCase().execute(user_id=current_user.id)
    )


@api.route("/v1/notifications/receive", methods=["PATCH"])
@jwt_required
@auth_required
@swag_from("update_receive_notification_setting.yml", methods=["PATCH"])
def update_receive_notification_setting_view():
    dto = UpdateReceiveNotificationSettingRequestSchema(
        **request.get_json(), user_id=current_user.id,
    ).validate_request_and_make_dto()

    return UpdateReceiveNotificationSettingPresenter().transform(
        UpdateReceiveNotificationSettingUseCase().execute(dto=dto)
    )
