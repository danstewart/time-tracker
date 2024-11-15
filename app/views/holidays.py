from flask import Blueprint, flash, redirect, url_for

from app.controllers import holidays, settings
from app.controllers.user.util import login_required
from app.lib.blocks import render
from app.lib.logger import get_logger

v = Blueprint("holidays", __name__)
logger = get_logger(__name__)


@v.get("/holidays")
@v.get("/holidays/upcoming")
@login_required
def upcoming_holidays():
    _settings = settings.fetch()

    if not _settings.holiday_location:
        flash("Please set a holiday location to view the holidays list.", "warning")
        return redirect(url_for("settings.general_settings"))

    return render(
        "pages/holidays.html.j2",
        page="upcoming",
        upcoming_holidays=holidays.get_upcoming_holidays(),
    )


@v.get("/holidays/history")
@login_required
def previous_holidays():
    _settings = settings.fetch()

    if not _settings.holiday_location:
        flash("Please set a holiday location to view the holidays list.", "warning")
        return redirect(url_for("settings.general_settings"))

    return render(
        "pages/holidays.html.j2",
        page="history",
        previous_holidays=holidays.get_previous_holidays(),
    )
