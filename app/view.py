import arrow
from flask import Blueprint
from flask import current_app as app
from flask import redirect, render_template, request

from app.controller import Settings, Time
from app.lib.database import pony
from app.lib.logger import get_logger

v = Blueprint("default", __name__)
logger = get_logger("view.py")


@app.context_processor
@pony.db_session
def inject_settings():
    return dict(settings=Settings().get())


@v.get("/")
def home():
    time = Time()
    stats = time.get_stats()
    time_entries = time.get_all()
    return render_template("pages/home.html.j2", time_entries=time_entries, tz=Time().tz, arrow=arrow, stats=stats)


@v.route("/settings", methods=["GET", "POST"])
def settings():
    settings = Settings()

    if request.form:
        settings.update(**request.form)

    return render_template("pages/settings.html.j2", settings=settings.settings)


@v.post("/time/add")
def add_time():
    if request.form:
        values = dict(request.form)
        clock = values.pop("clock")

        if clock == "manual":
            Time().create(**values)
        elif clock == "in":
            Time().create(start=values["time"])
        else:
            Time().clock_out(end=values["time"])

    return redirect("/")


@v.delete("/time/delete/<row_id>")
def delete_time(row_id):
    Time().delete(row_id)
    return "OK", 200


# FRAMES
@v.get("/frames/time-log-table")
def time_log_table():
    time = Time()
    time_entries = time.get_all()
    return render_template("frames/time_log_table.html.j2", time_entries=time_entries, tz=Time().tz, arrow=arrow)


@v.get("/frames/<frame>")
def render_frame(frame: str):
    return render_template("frames/{}.html.j2".format(frame))


@v.get("/lightboxes/<box>")
def render_lightbox(box: str):
    return render_template("lightboxes/{}.html.j2".format(box))
