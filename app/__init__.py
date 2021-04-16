from typing import Optional, Dict, Any

from flasgger import Swagger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.config import config
from app.extensions import jwt
from app.extensions.database import db, migrate
from app.extensions.ioc_container import init_provider
from app.extensions.swagger import swagger_config
from app.http.view.main import main as main_bp

from app.http.view import api

# event listener initialization
from core.domains.board import event


def init_config(
    app: Flask, config_name: str, settings: Optional[Dict[str, Any]] = None
) -> None:
    app_config = config[config_name]
    app.config.from_object(app_config)


def init_db(app: Flask, db: SQLAlchemy) -> None:
    db.init_app(app)
    migrate.init_app(app, db)


def init_blueprint(app: Flask):
    app.register_blueprint(main_bp)
    app.register_blueprint(api)


def init_extensions(app: Flask):
    Swagger(app, config=swagger_config)
    jwt.init_app(app)


def create_app(
    config_name: str = "default", settings: Optional[Dict[str, Any]] = None
) -> Flask:
    app = Flask(__name__)
    init_config(app, config_name, settings)

    print("\n💌💌💌Flask Config is '{}'".format(config_name))

    with app.app_context():
        init_blueprint(app)
        init_db(app, db)
        init_provider()
        init_extensions(app)

    return app
