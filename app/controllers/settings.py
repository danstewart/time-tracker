from app.lib.database import pony
from app.lib.logger import get_logger
from app.models import Settings

logger = get_logger(__name__)


@pony.db_session
def fetch() -> Settings:
    from app.controllers.user.util import get_user

    settings = Settings.get()

    if not settings:
        # These are the default settings
        settings = Settings(
            timezone="Europe/London",
            week_start=0,  # Monday
            hours_per_day=7.5,
            work_days="MTWTF--",
            user=get_user(),
        )
        pony.commit()
    return settings


@pony.db_session
def update(**values):
    """Updates the settings row"""
    settings = Settings.get()

    work_days = []
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        if values.get("work_day_" + day):
            work_days.append(day[0])
            values.pop("work_day_" + day)
        else:
            work_days.append("-")

    values["work_days"] = "".join(work_days)
    settings.set(**values)
    pony.commit()
