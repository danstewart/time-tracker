import arrow
from app.models import Time as TimeModel
from app.models import Settings as SettingsModel
from app.lib.database import pony
from app.lib.logger import get_logger
from typing import Iterator, Optional

logger = get_logger('controller.py')


class Settings:
    def __init__(self):
        self.settings = SettingsModel.get()

        if not self.settings:
            self.settings = SettingsModel(timezone="Europe/London")
            pony.commit()


    def get(self):
        """Returns the settings row"""
        return self.settings


    def update(self, **values):
        """Updates the settings row"""
        self.settings.set(**values)
        pony.commit()


class Time:
    def __init__(self):
        self.settings = Settings().get()
        self.tz = self.settings.timezone
        self.today = arrow.now(self.tz).format('YYYY-MM-DD')
        self.model = TimeModel


    def get_all(self) -> Iterator[TimeModel]:
        """Return all time records sorted by start date"""
        return self.model.select().order_by(pony.desc(self.model.start), pony.desc(self.model.id))


    def create(self, start: int, end: Optional[int] = None, date: Optional[str] = None) -> None:
        """Create a new time record"""
        if not date:
            date = self.today

        start = '{} {}'.format(date, start)
        start = int(arrow.get(start, tzinfo=self.tz).timestamp())

        if end:
            end = '{} {}'.format(date, end)
            end = int(arrow.get(end, tzinfo=self.tz).timestamp())

        return self.model(
            start=start,
            end=end if end else None,
            note="Testing",
        )


    def clock_out(self, end: int):
        """Sets the end time for the current time record"""
        end = '{} {}'.format(self.today, end)
        end = arrow.get(end, tzinfo=self.tz)

        current_record = (self.model.select()
            .filter(lambda t: t.end is None)
            .order_by(pony.desc(self.model.start))
            .first())

        current_record.end = int(end.timestamp())


    def delete(self, row_id: int):
        """Deletes a time record by ID"""
        if record := self.model.get(id=row_id):
            record.delete()
