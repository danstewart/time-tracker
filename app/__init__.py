from flask import Flask

from pony.flask import Pony
from app.models import Time  # noqa F401
from app.lib.database import db  # noqa F401


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config/app_config.py')

    Pony(app)
    db.connect()

    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.add_extension('jinja2.ext.debug')

    with app.app_context():
        from app import view
        app.register_blueprint(view.v)

    return app
