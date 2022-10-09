import os

from flask import Flask
from pony.flask import Pony

from app.lib.database import db, pony
from app.models import *  # noqa: F401


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config/app_config.py")

    app.config.update(
        SESSION_COOKIE_SECURE=not bool(os.getenv("FLASK_DEBUG")),  # Cookies are secure when not running debug mode
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    Pony(app)
    db.connect()
    pony.set_sql_debug(False)

    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.add_extension("jinja2.ext.loopcontrols")
    app.jinja_env.add_extension("jinja2.ext.debug")

    with app.app_context():
        from app.controllers.user.util import is_logged_in
        from app.lib.util.security import enable_csrf_protection, get_csrf_token
        from app.views import core, settings, time, user

        enable_csrf_protection(app)

        app.register_blueprint(time.v)
        app.register_blueprint(settings.v)
        app.register_blueprint(user.v)
        app.register_blueprint(core.v)

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
                "settings": None,
                "host": app.config["HOST"],
                "csrf_token": get_csrf_token,
            }

            if globals["is_logged_in"]:
                globals["settings"] = fetch()

            return globals

    return app
