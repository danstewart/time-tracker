import arrow

from app.lib.database import db, pony


class Time(db.Entity):
    id = pony.PrimaryKey(int, auto=True)
    start = pony.Required(int)
    end = pony.Optional(int)
    note = pony.Optional(str)

    breaks = pony.Set("Break")

    def logged(self):
        """
        Return the total duration of a time entry in seconds
        With any breaks removed
        """
        to_remove = sum([_break.end - _break.start for _break in self.breaks])
        end = self.end or arrow.utcnow().int_timestamp
        duration = end - self.start
        return duration - to_remove

    @classmethod
    def since(cls, timestamp):
        return pony.select(row for row in cls if row.start >= timestamp)


class Break(db.Entity):
    time = pony.Required(Time)
    start = pony.Required(int)
    end = pony.Optional(int)
    note = pony.Optional(str)


class Settings(db.Entity):
    id = pony.PrimaryKey(int, auto=True)
    timezone = pony.Required(str)
    week_start = pony.Required(int)
    hours_per_day = pony.Required(float)
    days_per_week = pony.Required(int)
