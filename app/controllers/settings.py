from app.lib.database import pony
from app.lib.logger import get_logger
from app.models import Settings

logger = get_logger(__name__)


@pony.db_session
def fetch() -> Settings:
    settings = Settings.get()

    if not settings:
        # These are the default settings
        settings = Settings(
            timezone="Europe/London",
            week_start=0,  # Monday
            hours_per_day=7.5,
        )
        pony.commit()
    return settings


@pony.db_session
def update(**values):
    """Updates the settings row"""
    settings = Settings.get()
    settings.set(**values)
    pony.commit()
