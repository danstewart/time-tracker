from flask import Blueprint, render_template

from app.controllers import time
from app.controllers.user.util import login_required
from app.lib.logger import get_logger

v = Blueprint("holidays", __name__)
logger = get_logger(__name__)


@v.get("/holidays")
@login_required
def upcoming_holidays():
    # If request is coming from a DynamicFrame then only render the `content` block
    # TODO:
    # - Turn this into a decorator
    # - Send the header from dynamic frames
    from flask import request

    from app.lib.blocks import render_block

    if request.headers.get("X-DynamicFrame"):
        return render_block(
            "pages/holidays/upcoming.html.j2",
            "content",
            upcoming_holidays=time.get_upcoming_holidays(),
            page="upcoming",
        )

    return render_template(
        "pages/holidays/upcoming.html.j2",
        page="upcoming",
        upcoming_holidays=time.get_upcoming_holidays(),
    )


@v.get("/holidays/history")
@login_required
def previous_holidays():
    from flask import request

    from app.lib.blocks import render_block

    if request.headers.get("X-DynamicFrame"):
        return render_block(
            "pages/holidays/history.html.j2",
            "content",
            previous_holidays=time.get_previous_holidays(),
            page="history",
        )

    return render_template(
        "pages/holidays/history.html.j2",
        page="history",
        previous_holidays=time.get_previous_holidays(),
    )
