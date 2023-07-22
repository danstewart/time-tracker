from flask import Blueprint, flash, redirect, render_template, url_for

from app.controllers import holidays, settings
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

    _settings = settings.fetch()

    if not _settings.holiday_location:
        flash("Please set a holiday location to view the holidays list", "warning")
        return redirect(url_for("settings.general_settings"))

    if request.headers.get("X-DynamicFrame"):
        return render_block(
            "pages/holidays/upcoming.html.j2",
            "content",
            upcoming_holidays=holidays.get_upcoming_holidays(),
            page="upcoming",
        )

    return render_template(
        "pages/holidays/upcoming.html.j2",
        page="upcoming",
        upcoming_holidays=holidays.get_upcoming_holidays(),
    )


@v.get("/holidays/history")
@login_required
def previous_holidays():
    from flask import request

    from app.lib.blocks import render_block

    _settings = settings.fetch()

    if not _settings.holiday_location:
        flash("Please set a holiday location to view the holidays list", "warning")
        return redirect(url_for("settings.general_settings"))

    if request.headers.get("X-DynamicFrame"):
        return render_block(
            "pages/holidays/history.html.j2",
            "content",
            previous_holidays=holidays.get_previous_holidays(),
            page="history",
        )

    return render_template(
        "pages/holidays/history.html.j2",
        page="history",
        previous_holidays=holidays.get_previous_holidays(),
    )
