from flask import Flask
from pony.flask import Pony

from app.lib.database import db, pony
from app.models import Settings, Time


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config/app_config.py")

    Pony(app)
    db.connect()

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
        def inject_settings():
            from app.controllers.settings import fetch

            return dict(settings=fetch())

    return app
