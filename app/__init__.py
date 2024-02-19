import os

import highlight_io
from flask import Flask, render_template
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from highlight_io.integrations.flask import FlaskIntegration

from app.lib.util.lenient import lenient_wrap

db = SQLAlchemy()
migrate = Migrate()
cors = CORS(
    expose_headers=["X-Highlight-Request"],
    allow_headers=["X-Highlight-Request"],
)


def create_app(test_mode: bool = False):
    app = Flask(__name__)
    app.config.from_pyfile("../config/app_config.py")

    app.config.update(
        SESSION_COOKIE_SECURE=not bool(os.getenv("FLASK_DEBUG")),  # Cookies are secure when not running debug mode
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # Initialise database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/app/log-my-time/db/time.db"

    if test_mode or os.getenv("TEST_MODE") == "yes":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/app/log-my-time/db/time.test.db"

    cors.init_app(app)
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
        from app.views import core, holidays, leave, settings, time, user

        enable_csrf_protection(app)

        app.register_blueprint(time.v)
        app.register_blueprint(leave.v)
        app.register_blueprint(settings.v)
        app.register_blueprint(user.v)
        app.register_blueprint(core.v)
        app.register_blueprint(data.v)
        app.register_blueprint(holidays.v)

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
                "HIGHLIGHT_IO_PROJECT": app.config.get("HIGHLIGHT_IO_PROJECT"),
            }

            if globals["is_logged_in"]:
                globals["settings"] = fetch()

            return globals

        if os.getenv("TEST_MODE") != "yes" and app.config.get("HIGHLIGHT_IO_PROJECT"):
            # Initialise highlight.io - unless in test mode
            H = highlight_io.H(
                app.config["HIGHLIGHT_IO_PROJECT"],
                integrations=[FlaskIntegration()],
                instrument_logging=True,
                service_name="LogMyTime",
                service_version="commit:123",
                environment="local",
            )

    @app.errorhandler(Exception)
    def handle_error(exc):
        highlight_io.H.get_instance().record_exception(exc)
        return render_template("pages/error.html.j2", error=exc), 503

    return app
