from flask import jsonify
from flask_jwt_extended import jwt_required

from app.__meta__ import __api_name__, __version__
from app.http.view import auth_required, api


@api.route("/main", methods=["GET"])
@jwt_required
@auth_required
def index():
    return jsonify({"name": __api_name__, "version": __version__})
