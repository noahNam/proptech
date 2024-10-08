import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "auckland"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_BINDS = {"read_only": "sqlite:///:memory:"}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_PRE_PING = True
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": SQLALCHEMY_PRE_PING}
    DEBUG = False

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "hawaii"
    # JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://127.0.0.1:6379"

    # Naver Cloud Platform Environment
    SENS_SID = os.environ.get("SENS_SID") or ""
    NCP_ACCESS_KEY = os.environ.get("NCP_ACCESS_KEY") or ""
    NCP_SECRET_KEY = os.environ.get("NCP_SECRET_KEY") or ""

    # AWS ENV
    AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY") or "AKIA5IBYL2SRU6O3XLE4"
    AWS_SECRET_ACCESS_KEY = (
        os.environ.get("AWS_SECRET_ACCESS_KEY")
        or "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"
    )
    AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME") or "ap-northeast-2"

    # SQS
    SQS_BASE = os.environ.get("SQS_BASE") or ""
    SQS_USER_DATA_SYNC_TO_LAKE = os.environ.get("SQS_USER_DATA_SYNC_TO_LAKE") or ""

    # Ironman service
    IRONMAN_SERVICE_URL = os.environ.get("IRONMAN_SERVICE_URL") or ""

    # Celery
    BACKEND_RESULT = (
        os.environ.get("BACKEND_RESULT")
        or "db+mysql+pymysql://apartalk_admin:!wjstngks117@localhost:3306/apartalk_data_mart"
    )
    TIMEZONE = "Asia/Seoul"
    CELERY_ENABLE_UTC = False


class LocalConfig(Config):
    os.environ["FLASK_ENV"] = "local"
    SENTRY_ENVIRONMENT = "local"
    SQLALCHEMY_ECHO = True
    DEBUG = True

    # Local environment configuration using Docker API service
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://toadhome_tanos:!Dkvkxhr117@localhost:5432/tanos"
    )
    SQLALCHEMY_BINDS = {
        "read_only": "postgresql+psycopg2://toadhome_tanos:!Dkvkxhr117@localhost:5432/tanos"
    }
    # Prod migrate
    # SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://postgres:%s@localhost:5432/tanos" % urlquote("password")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_BINDS = {"read_only": "sqlite:///:memory:"}

    WTF_CSRF_ENABLED = False


class DevelopmentConfig(Config):
    os.environ["FLASK_ENV"] = "development"
    SENTRY_ENVIRONMENT = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or "sqlite:///:memory:"
    SENTRY_KEY = os.environ.get("SENTRY_KEY")
    SQLALCHEMY_BINDS = {"read_only": SQLALCHEMY_DATABASE_URI}


class ProductionConfig(Config):
    os.environ["FLASK_ENV"] = "production"
    SENTRY_ENVIRONMENT = "production"
    SENTRY_KEY = os.environ.get("SENTRY_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("PROD_DATABASE_URL")
    SQLALCHEMY_BINDS = {"read_only": os.environ.get("PROD_DATABASE_READONLY_PROXY_URL")}


config = dict(
    default=LocalConfig,
    local=LocalConfig,
    testing=TestConfig,
    development=DevelopmentConfig,
    prod=ProductionConfig,
)
