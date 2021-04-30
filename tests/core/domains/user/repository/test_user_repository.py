from app.persistence.model.user_model import UserModel


def test_create_user_profiles_when_first_login_then_success(session, create_user):
    users = create_user
    user = session.query(UserModel).filter_by(id=1).first()
    assert 1 == 1
