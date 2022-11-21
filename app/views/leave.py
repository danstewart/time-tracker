from typing import Optional

from flask import Blueprint, render_template, request

from app.controllers import leave
from app.controllers.user.util import login_required
from app.lib.logger import get_logger

v = Blueprint("leave", __name__)
logger = get_logger(__name__)


@v.route("/frames/leave_form/", methods=["GET", "POST"])
@v.route("/frames/leave_form/<int:row_id>", methods=["GET", "POST"])
@login_required
def leave_form(row_id: Optional[int] = None):
    if request.method == "POST" and request.json:
        if row_id:
            leave.update(
                row_id,
                leave_type="annual",
                start=request.json["start"],
                duration=request.json["duration"],
                note=request.json["note"],
            )
        else:
            leave.create(
                leave_type="annual",
                start=request.json["start"],
                duration=request.json["duration"],
                note=request.json["note"],
            )

        return "", 200

    return render_template(
        "frames/leave_form.html.j2",
        row_id=row_id,
    )
