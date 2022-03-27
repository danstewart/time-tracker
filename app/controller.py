from typing import Dict, Iterator, Optional

import arrow

from app.lib.database import pony
from app.lib.logger import get_logger
from app.models import Settings as SettingsModel
from app.models import Time as TimeModel

logger = get_logger("controller.py")


class Settings:
    def __init__(self):
        self.settings = SettingsModel.get()

        if not self.settings:
            # These are the default settings
            self.settings = SettingsModel(
                timezone="Europe/London",
                week_start=0,  # Monday
                hours_per_day=7.5,
            )
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
        self.today = arrow.now(self.tz).format("YYYY-MM-DD")
        self.model = TimeModel

    def get_all(self) -> Iterator[TimeModel]:
        """Return all time records sorted by start date"""
        return self.model.select().order_by(pony.desc(self.model.start), pony.desc(self.model.id))

    def get_stats(self) -> Dict:
        """Return the header stats"""
        from app.lib.util.date import humanize_seconds

        now = arrow.now(tz=self.settings.timezone)
        today = now.replace(hour=0, minute=0)
        if now.weekday() != self.settings.week_start:
            start = today.shift(weekday=self.settings.week_start).shift(days=-7)
        else:
            start = today

        # Time logged this week
        logged_this_week = sum([rec.logged() for rec in self.model.since(start.int_timestamp)])

        # Time left to log today
        todo_today = 0
        if today.weekday() < 5:
            logged_today = sum([rec.logged() for rec in self.model.since(today.int_timestamp)])
            todo_today = (self.settings.hours_per_day * 60 * 60) - logged_today

        # Overtime (all time)
        overtime = 0
        overtime_prefix = ""
        if first_record := self.model.select().order_by(self.model.start).first():
            from app.lib.util.date import calculate_expected_hours

            first_day = arrow.get(first_record.start).to(self.settings.timezone)
            expected_hours = calculate_expected_hours(
                start=first_day,
                end=today,
                hours_per_day=self.settings.hours_per_day,
            )

            overtime = -(expected_hours * 60 * 60)  # Convert to seconds
            if total_logged := pony.select(sum(row.end - row.start) for row in self.model).first():
                overtime += total_logged

            if overtime > 0:
                overtime_prefix = "+"
            elif overtime < 0:
                overtime_prefix = "-"

        return {
            "logged_this_week": humanize_seconds(seconds=logged_this_week),
            "hours_left_today": humanize_seconds(todo_today),
            "overtime": "{}{}".format(overtime_prefix, humanize_seconds(seconds=overtime)),
        }

    def create(
        self, start: int, end: Optional[int] = None, date: Optional[str] = None, note: Optional[str] = ""
    ) -> TimeModel:
        """Create a new time record"""
        if not date:
            date = self.today

        start_dt = "{} {}".format(date, start)
        start_dt = arrow.get(start_dt, tzinfo=self.tz).int_timestamp

        end_dt = None
        if end:
            end_dt = "{} {}".format(date, end)
            end_dt = arrow.get(end, tzinfo=self.tz).int_timestamp

        return self.model(
            start=start_dt,
            end=end_dt,
            note=note,
        )

    def clock_out(self, end: int):
        """Sets the end time for the current time record"""
        end_dt = "{} {}".format(self.today, end)
        end_dt = arrow.get(end_dt, tzinfo=self.tz)

        current_record = (
            self.model.select().filter(lambda t: t.end is None).order_by(pony.desc(self.model.start)).first()
        )

        current_record.end = end_dt.int_timestamp
        current_record.logged = end_dt.int_timestamp - current_record.start

    def delete(self, row_id: int):
        """Deletes a time record by ID"""
        if record := self.model.get(id=row_id):
            record.delete()
