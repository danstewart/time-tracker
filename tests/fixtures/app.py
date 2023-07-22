def app():
    from app import create_app

    app = create_app()

    with app.app_context(), app.test_request_context():
        yield app
