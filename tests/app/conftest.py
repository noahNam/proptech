import pytest
from flask_jwt_extended import JWTManager, create_access_token


@pytest.fixture()
def make_header():
    def _make_header(
        authorization: str = None,
        content_type: str = "application/json",
        accept: str = "application/json",
    ):
        return {
            "Authorization": authorization,
            "Content-Type": content_type,
            "Accept": accept,
        }

    return _make_header


@pytest.fixture()
def make_authorization():
    def _make_authorization(user_id: int = None):
        access_token = create_access_token(identity=user_id)
        return "Bearer " + access_token

    return _make_authorization


@pytest.fixture()
def client(app):
    app.testing = True
    return app.test_client()


@pytest.fixture()
def test_request_context(app):
    return app.test_request_context()


@pytest.fixture()
def jwt_manager(app):
    return JWTManager(app)
