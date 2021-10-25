import os
import sentry_sdk
from typing import Optional, Dict, Any

from flasgger import Swagger
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from flask_sqlalchemy import SQLAlchemy

from app.commands import init_commands
from app.config import config
from app.extensions import jwt, sms, redis, cors
from app.extensions.database import db, migrate
from app.extensions.ioc_container import init_provider
from app.extensions.swagger import swagger_config
from app.http.view import api

# alembic auto-generate detected
# from app.persistence.model import *


# event listener initialization
from core.domains.user import event
from core.domains.notification import event
from core.domains.house import event
from core.domains.banner import event
from core.domains.payment import event
from core.domains.report import event


def init_config(
    app: Flask, config_name: str, settings: Optional[Dict[str, Any]] = None
) -> None:
    app_config = config[config_name]
    app.config.from_object(app_config)


def init_db(app: Flask, db: SQLAlchemy) -> None:
    db.init_app(app)
    migrate.init_app(app, db)


def init_blueprint(app: Flask):
    app.register_blueprint(api, url_prefix="/api/tanos")


def init_extensions(app: Flask):
    Swagger(app, **swagger_config())
    jwt.init_app(app)
    sms.init_app(app)
    redis.init_app(app)
    cors.init_app(
        app, resources={r"*": {"origins": app.config.get("IRONMAN_SERVICE_URL")}}
    )


def init_sentry(app: Flask):
    if app.config.get("SENTRY_KEY", None):
        sentry_sdk.init(
            dsn=app.config.get("SENTRY_KEY"),
            integrations=[FlaskIntegration(), RedisIntegration()],
            environment=app.config.get("SENTRY_ENVIRONMENT"),
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0,
        )


def create_app(
    config_name: str = "default", settings: Optional[Dict[str, Any]] = None
) -> Flask:
    app = Flask(__name__)

    if (
        os.environ.get("FLASK_CONFIG") is not None
        and os.environ.get("FLASK_CONFIG") is not config_name
    ):
        config_name = os.environ.get("FLASK_CONFIG")

    init_config(app, config_name, settings)

    with app.app_context():
        init_blueprint(app)
        init_db(app, db)
        init_provider(app)
        init_extensions(app)
        init_sentry(app)
        init_commands()

    print("\n💌💌💌Flask Config is '{}'".format(config_name))

    return app
