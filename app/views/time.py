import arrow
from app.controllers import settings, time
from app.lib.logger import get_logger
from flask import Blueprint
from flask import current_app as app
from flask import redirect, render_template, request

v = Blueprint("time", __name__)
logger = get_logger(__name__)

_settings = settings.fetch()


@v.get("/")
def home():
    stats = time.stats()
    time_entries = time.all()
    return render_template(
        "pages/home.html.j2", time_entries=time_entries, tz=_settings.timezone, arrow=arrow, stats=stats
    )


@v.post("/time/add")
def add_time():
    if request.form:
        values = dict(request.form)
        clock = values.pop("clock")

        if clock == "manual":
            time.create(start=values["start"], end=values["end"] if "end" in values else None, note=values["note"])
        elif clock == "in":
            time.create(start=values["time"])
        else:
            time.clock_out(end=values["time"])

    return redirect("/")


@v.delete("/time/delete/<row_id>")
def delete_time(row_id):
    time.delete(row_id)
    return "OK", 200


# FRAMES
@v.get("/frames/time-log-table")
def time_log_table():
    time_entries = time.all()
    return render_template(
        "frames/time_log_table.html.j2", time_entries=time_entries, tz=_settings.timezone, arrow=arrow
    )


@v.route("/frames/time_form/", methods=["GET", "POST"])
@v.route("/frames/time_form/<row_id>", methods=["GET", "POST"])
def time_form(row_id: str = ""):
    if request.method == "POST" and request.json:
        if row_id:
            time.update(
                row_id,
                start=request.json["start"],
                end=request.json["end"],
                note=request.json["note"],
            )
        else:
            time.create(
                start=request.json["start"],
                end=request.json["end"],
                note=request.json["note"],
            )
        return "", 200

    return render_template(
        "frames/time_form.html.j2", row_id=row_id, values=time.get(row_id).to_dict() if row_id else {}
    )
