from flask import Blueprint, render_template

from app.controllers import time
from app.controllers.user.util import login_required
from app.lib.logger import get_logger

v = Blueprint("holidays", __name__)
logger = get_logger(__name__)


@v.get("/holidays")
@login_required
def holiday_summary():
    return render_template(
        "pages/holidays/upcoming.html.j2",
        page="upcoming",
        next_public_holiday=time.get_next_public_holiday(),
    )
