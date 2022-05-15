from flask import Flask
from pony.flask import Pony

from app.lib.database import db, pony
from app.models import Settings, Time


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config/app_config.py")

    Pony(app)
    db.connect()
    pony.set_sql_debug(False)

    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.add_extension("jinja2.ext.loopcontrols")
    app.jinja_env.add_extension("jinja2.ext.debug")

    with app.app_context():
        from app.views import core, settings, time

        app.register_blueprint(time.v)
        app.register_blueprint(settings.v)
        app.register_blueprint(core.v)

        # Inject our settings into all templates
        @app.context_processor
        def inject_globals():
            import arrow

            from app.controllers.settings import fetch
            from app.lib.util.date import humanize_seconds

            user_settings = fetch()
            return dict(settings=user_settings, arrow=arrow, humanize_seconds=humanize_seconds)

    return app
