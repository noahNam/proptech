from flasgger import swag_from
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.http.view.authentication import current_user

from app.extensions.utils.auth_helper import get_renew_token
from app.http.requests.v1.auth_request import MobileAuthSmsSendSchemeRequest, MobileAuthSmsConfirmSchemeRequest
from app.http.responses.presenters.v1.auth_presenter import (
    AuthenticationPresenter, AuthSmsSendPresenter, AuthSmsConfirmPresenter,
)
from app.http.view import api
from app.http.view.authentication import auth_required
from core.domains.authentication.use_case.v1.auth_use_case import (
    AuthenticationUseCase, MobileAuthSendSmsUseCase, MobileAuthConfirmSmsUseCase,
)


@api.route("/auth/v1/", methods=["GET"])
@jwt_required
@auth_required
def auth_for_testing_view():
    """
    인증 테스트 뷰
    """
    return AuthenticationPresenter().transform(AuthenticationUseCase().execute())


@api.route("/v1/token/update", methods=["GET"])
@jwt_required
def token_refresh_view():
    """
        토큰 업데이트 테스트용 뷰
    """
    auth_header = request.headers.get("Authorization")
    bearer, _, token = auth_header.partition(" ")

    data = get_renew_token(token).json()

    return jsonify(access_token=data["data"]["token_info"]["access_token"], status="success")


@api.route("/v1/auth/sms/send", methods=["POST"])
@jwt_required
@auth_required
@swag_from("auth_send_sms_view.yml", methods=["POST"])
def mobile_auth_sms_send_view():
    dto = MobileAuthSmsSendSchemeRequest(
        **request.get_json(),
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return AuthSmsSendPresenter().transform(MobileAuthSendSmsUseCase().execute(dto=dto))


@api.route("/v1/auth/sms/confirm", methods=["POST"])
@jwt_required
@auth_required
@swag_from("auth_confirm_sms_view.yml", methods=["POST"])
def mobile_auth_sms_confirm_view():
    dto = MobileAuthSmsConfirmSchemeRequest(
        **request.get_json(),
        user_id=current_user.id,
    ).validate_request_and_make_dto()

    return AuthSmsConfirmPresenter().transform(MobileAuthConfirmSmsUseCase().execute(dto=dto))
