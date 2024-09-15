import pytest


@pytest.fixture
def app():
    from app import Model, create_app, db

    app = create_app(test_mode=True)

    with app.app_context(), app.test_request_context():
        engine = db.engine

    # Create tables
    Model.metadata.create_all(engine)

    # Add any necessary test data
    from app.models import User

    test_user = User(email="test@example.com")
    db.session.add(test_user)

    test_user.set_password("test")
    test_user.verify()

    yield app
