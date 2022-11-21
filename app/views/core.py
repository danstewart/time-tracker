from flask import Blueprint, render_template

from app.controllers import time
from app.controllers.user.util import login_required
from app.lib.logger import get_logger

v = Blueprint("core", __name__)
logger = get_logger(__name__)


@v.get("/")
@login_required
def home():
    return render_template(
        "pages/home.html.j2",
        week_list=time.week_list(),
    )


@v.get("/about")
def about_page():
    return render_template("pages/about.html.j2")
