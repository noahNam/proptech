import os
from urllib.parse import quote as urlquote


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "auckland"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False
    DEBUG = False

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "hawaii"

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379"

    # Naver Cloud Platform Environment
    SENS_SID = os.environ.get("SENS_SID") or "ncp:sms:kr:268333493425:test-apartalk"
    NCP_ACCESS_KEY = os.environ.get("NCP_ACCESS_KEY") or "g4yBBz9JRbfEsEiN7PM0"
    NCP_SECRET_KEY = (
        os.environ.get("NCP_SECRET_KEY") or "p8InI44k4bp15jVod2xynDGGBSdZMuqlvLy8vuCM"
    )


class LocalConfig(Config):
    os.environ["FLASK_ENV"] = "local"
    SENTRY_ENVIRONMENT = "local"
    SQLALCHEMY_ECHO = True
    DEBUG = True
    # Local environment configuration using Docker API service
    # SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:1234@postgres:5432/tanos"
    # Prod migrate
    # SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://postgres:%s@localhost:5432/tanos" % urlquote("password")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
    )

    WTF_CSRF_ENABLED = False


class DevelopmentConfig(Config):
    os.environ["FLASK_ENV"] = "development"
    SENTRY_ENVIRONMENT = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or "sqlite:///:memory:"
    SENTRY_KEY = os.environ.get("SENTRY_KEY")


class ProductionConfig(Config):
    os.environ["FLASK_ENV"] = "production"
    SENTRY_ENVIRONMENT = "production"
    SENTRY_KEY = os.environ.get("SENTRY_KEY")


config = dict(
    default=LocalConfig,
    local=LocalConfig,
    testing=TestConfig,
    development=DevelopmentConfig,
    prod=ProductionConfig,
)
