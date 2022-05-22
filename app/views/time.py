from app.controllers import settings, time
from app.controllers.user.util import login_required
from app.lib.logger import get_logger
from app.lib.util.date import humanize_seconds
from flask import Blueprint
from flask import current_app as app
from flask import redirect, render_template, request

v = Blueprint("time", __name__)
logger = get_logger(__name__)


@v.get("/")
@login_required
def home():
    return render_template(
        "pages/home.html.j2",
    )


@v.post("/time/add")
@login_required
def add_time():
    if request.form:
        values = dict(request.form)
        clock = values.pop("clock")

        match clock:
            case "manual":
                time.create(start=values["start"], end=values["end"] if "end" in values else None, note=values["note"])
            case "in":
                time.create(start=values["time"])
            case "out":
                time.clock_out(end=values["time"])
            case "break:start":
                time.break_start(start=values["time"])
            case "break:end":
                time.break_end(end=values["time"])

    return redirect("/")


@v.delete("/time/delete/<row_id>")
@login_required
def delete_time(row_id):
    time.delete(row_id)
    return "OK", 200


# FRAMES
@v.get("/frames/time-log-table")
@login_required
def time_log_table():
    time_entries = time.all()
    return render_template("frames/time_log_table.html.j2", time_entries=time_entries)


@v.get("/frames/time-stats")
@login_required
def time_stats():
    time_stats = time.stats()
    return render_template("frames/time_stats.html.j2", stats=time_stats)


@v.get("/frames/clock_in_form")
@login_required
def clock_in_form():
    time_entries = time.all()

    clocked_in = time_entries.first() and not time_entries.first().end
    on_break = time_entries.first() and time_entries.first().breaks.filter(lambda b: not b.end)

    return render_template("frames/clock_in_form.html.j2", clocked_in=clocked_in, on_break=on_break)


@v.route("/frames/time_form/", methods=["GET", "POST"])
@v.route("/frames/time_form/<row_id>", methods=["GET", "POST"])
@login_required
def time_form(row_id: str = ""):
    if request.method == "POST" and request.json:
        from collections import defaultdict

        if row_id:
            time.update(
                row_id,
                start=request.json["start"],
                end=request.json["end"],
                note=request.json["note"],
            )

            breaks = defaultdict(dict)
            for key, value in request.json.items():
                if key.startswith("break-"):
                    _, field, break_id = key.split("-")
                    breaks[break_id][field] = value

            time.bulk_update(table="break", data=breaks)
        else:
            time.create(
                start=request.json["start"],
                end=request.json["end"],
                note=request.json["note"],
            )
        return "", 200

    return render_template(
        "frames/time_form.html.j2",
        row_id=row_id,
        time=time.get(row_id) if row_id else None,
    )
