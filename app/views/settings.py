from app.controllers import settings
from app.lib.logger import get_logger
from flask import Blueprint, render_template, request

v = Blueprint("settings", __name__)
logger = get_logger(__name__)


@v.route("/settings", methods=["GET", "POST"])
def form():
    if request.form:
        settings.update(**request.form)

    return render_template("pages/settings.html.j2", settings=settings.fetch())
