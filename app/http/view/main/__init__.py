from flask import jsonify

from app.__meta__ import __version__
from app.http.view import api


@api.route("/main/health_check", methods=["GET"])
def index():
    return jsonify({"version": __version__})
