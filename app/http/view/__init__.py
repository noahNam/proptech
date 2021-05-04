from flask import Blueprint

api: Blueprint = Blueprint(name="api/tanos", import_name=__name__)

from .authentication.v1.auth_view import *  # noqa isort:skip
from .user.v1.user_view import *  # noqa isort:skip
