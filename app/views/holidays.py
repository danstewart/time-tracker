from flask import Blueprint, render_template

from app.controllers import time
from app.controllers.user.util import login_required
from app.lib.logger import get_logger

v = Blueprint("holidays", __name__)
logger = get_logger(__name__)


@v.get("/holidays")
@login_required
def holiday_summary():
    from flask import request

    from app.lib.blocks import render_block

    # If request is coming from a DynamicFrame then only render the `content` block
    # TODO:
    # - Turn this into a decorator
    # - Send the header from dynamic frames
    if request.headers.get("X-DynamicFrame"):
        return render_block(
            "pages/holidays/upcoming.html.j2",
            "content",
            next_public_holiday=time.get_next_public_holiday(),
            page="upcoming",
        )

    return render_template(
        "pages/holidays/upcoming.html.j2",
        page="upcoming",
        next_public_holiday=time.get_next_public_holiday(),
    )
