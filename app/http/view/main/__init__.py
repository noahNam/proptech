from flask import jsonify

from app.__meta__ import __api_name__, __version__
from app.http.view import api


@api.route("/main/heath_check", methods=["GET"])
def index():
    return jsonify({"name": __api_name__, "version": __version__})
