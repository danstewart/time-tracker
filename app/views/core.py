from flask import Blueprint, render_template, request

from app.controllers import leave, time
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


# FRAMES
@v.get("/frames/entries")
@login_required
def time_log_table():
    week_number = request.args.get("week")

    time_entries = time.all_for_week(week_number)
    leave_entries = leave.all_for_week(week_number)

    records = sorted((time_entries + leave_entries), key=lambda x: x.start, reverse=True)

    return render_template("frames/entries_table.html.j2", records=records, type_of=lambda thing: type(thing).__name__)
