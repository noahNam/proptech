from flasgger import swag_from
from flask import request

from app.http.requests.v1.house_request import UpsertInterestHouseRequestSchema
from app.http.responses.presenters.v1.house_presenter import UpsertInterestHousePresenter
from app.http.view import auth_required, api, current_user, jwt_required
from core.domains.house.use_case.v1.house_use_case import UpsertInterestHouseUseCase


@api.route("/v1/houses/<int:house_id>/like", methods=["POST"])
@jwt_required
@auth_required
@swag_from("update_notification.yml", methods=["POST"])
def upsert_interest_house_view(house_id):
    dto = UpsertInterestHouseRequestSchema(
        house_id=house_id, user_id=current_user.id, **request.get_json()
    ).validate_request_and_make_dto()

    return UpsertInterestHousePresenter().transform(UpsertInterestHouseUseCase().execute(dto=dto))
