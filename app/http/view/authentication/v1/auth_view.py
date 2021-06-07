from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions.utils.auth_helper import get_renew_token
from app.http.responses.presenters.v1.authentication_presenter import (
    AuthenticationPresenter,
)
from app.http.view import api
from app.http.view.authentication import auth_required
from core.domains.authentication.use_case.v1.authentication_use_case import (
    AuthenticationUseCase,
)


@api.route("/authentication/v1/", methods=["GET"])
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

    return jsonify(access_token=data["data"]["token_info"]["access_token"])
