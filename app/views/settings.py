from app.controllers import settings
from app.lib.logger import get_logger
from flask import Blueprint, render_template, request

v = Blueprint("settings", __name__)
logger = get_logger(__name__)


@v.route("/settings", methods=["GET", "POST"])
def form():
    if request.form:
        from flask import flash, redirect

        settings.update(**request.form)
        flash("Settings saved", "success")
        return redirect("/")

    return render_template("pages/settings.html.j2", settings=settings.fetch())
