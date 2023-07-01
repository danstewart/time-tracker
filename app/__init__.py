import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.lib.util.lenient import lenient_wrap

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config/app_config.py")

    app.config.update(
        SESSION_COOKIE_SECURE=not bool(os.getenv("FLASK_DEBUG")),  # Cookies are secure when not running debug mode
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # Initialise database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/app/log-my-time/db/time.db"

    if os.getenv("TEST_MODE") == "yes":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/app/log-my-time/db/time.test.db"

    db.init_app(app)
    db.metadata.naming_convention = {
        "ix": "ix_%(table_name)s_%(column_0_N_label)s",
        "uq": "uc_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    migrate.init_app(app, db)

    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.add_extension("jinja2.ext.loopcontrols")
    app.jinja_env.add_extension("jinja2.ext.debug")
    app.jinja_env.globals["lenient_wrap"] = lenient_wrap

    with app.app_context():
        from app.cli import data
        from app.controllers.user.util import is_admin, is_logged_in, unseen_whats_new
        from app.lib.util.security import enable_csrf_protection, get_csrf_token
        from app.views import core, leave, settings, time, user

        enable_csrf_protection(app)

        app.register_blueprint(time.v)
        app.register_blueprint(leave.v)
        app.register_blueprint(settings.v)
        app.register_blueprint(user.v)
        app.register_blueprint(core.v)
        app.register_blueprint(data.v)

        # Inject some values into ALL templates
        @app.context_processor
        def inject_globals():
            import arrow

            from app.controllers.settings import fetch
            from app.lib.util.date import humanize_seconds

            globals = {
                "arrow": arrow,
                "humanize_seconds": humanize_seconds,
                "is_logged_in": is_logged_in(),
                "is_admin": is_logged_in() and is_admin(),
                "unseen_whats_new": is_logged_in() and unseen_whats_new(),
                "settings": None,
                "host": app.config["HOST"],
                "csrf_token": get_csrf_token,
                "FLASK_DEBUG": os.getenv("FLASK_DEBUG") == "1",
            }

            if globals["is_logged_in"]:
                globals["settings"] = fetch()

            return globals

    return app
