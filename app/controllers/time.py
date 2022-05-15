from typing import Iterator, Optional

import arrow
from app.controllers import settings
from app.lib.database import pony
from app.lib.logger import get_logger
from app.models import Break, Time
from app.viewmodels import TimeStats

logger = get_logger(__name__)


_settings = settings.fetch()
_tz = _settings.timezone


@pony.db_session
def get(row_id: str) -> Time:
    return Time[row_id]


@pony.db_session
def all() -> Iterator[Time]:
    """Return all time records sorted by start date"""
    return Time.select().order_by(pony.desc(Time.start), pony.desc(Time.id))


@pony.db_session
def create(start: str, end: Optional[str] = None, date: Optional[str] = None, note: str = "") -> Time:
    """Create a new time record"""
    start_dt = arrow.get(start, tzinfo=_tz).int_timestamp

    end_dt = None
    if end:
        end_dt = arrow.get(end, tzinfo=_tz).int_timestamp

    return Time(
        start=start_dt,
        end=end_dt,
        note=note,
    )


@pony.db_session
def update(row_id: str, start: str, end: Optional[str] = None, note: str = "") -> Time:
    start_dt = arrow.get(start, tzinfo=_tz).int_timestamp

    end_dt = None
    if end:
        end_dt = arrow.get(end, tzinfo=_tz).int_timestamp

    t = Time[row_id]
    t.start = start_dt
    t.end = end_dt
    t.note = note
    return t


@pony.db_session
def delete(row_id: int) -> bool:
    """
    Deletes a time record by ID
    Returns True if deleted and False if not
    """
    if record := Time.get(id=row_id):
        record.delete()
        return True
    return False


@pony.db_session
def clock_out(end: str):
    """Sets the end time for the current time record"""
    end_dt = arrow.get(end, tzinfo=_tz)

    current_record = Time.select().filter(lambda t: t.end is None).order_by(pony.desc(Time.start)).first()

    current_record.end = end_dt.int_timestamp
    current_record.logged = end_dt.int_timestamp - current_record.start


@pony.db_session
def break_start(start: str):
    """Sets the start time for the current time record"""
    start_dt = arrow.get(start, tzinfo=_tz)

    current_record = Time.select().filter(lambda t: t.end is None).order_by(pony.desc(Time.start)).first()

    current_record.breaks.add(Break(time=current_record, start=start_dt.int_timestamp))


@pony.db_session
def break_end(end: str):
    """Sets the start time for the current time record"""
    end_dt = arrow.get(end, tzinfo=_tz)

    current_record = Time.select().filter(lambda t: t.end is None).order_by(pony.desc(Time.start)).first()

    current_break = current_record.breaks.filter(lambda b: not b.end)
    if current_break.first():
        current_break.first().end = end_dt.int_timestamp


@pony.db_session
def bulk_update(table, data: dict[int, dict]):
    """
    Updates multiple time records at once

    `table`: "time" or "break"
    `data`: A dict of {row_id: {column1: value1, column2: value2}}
    """
    model = Time if table == "time" else Break

    for row_id, row in data.items():
        for key, value in row.items():
            # Convert string dates to int timestamps
            if key in ("start", "end"):
                value = arrow.get(value, tzinfo=_tz).int_timestamp
            setattr(model[row_id], key, value)

    pony.commit()


@pony.db_session
def stats() -> TimeStats:
    """Return the weekly stats"""
    from app.lib.util.date import humanize_seconds

    now = arrow.now(tz=_tz)
    today = now.replace(hour=0, minute=0)
    if now.weekday() != _settings.week_start:
        start = today.shift(weekday=_settings.week_start).shift(days=-7)
    else:
        start = today

    # Time logged
    logged_today = sum([rec.logged() for rec in Time.since(today.int_timestamp)])
    logged_this_week = sum([rec.logged() for rec in Time.since(start.int_timestamp)])

    # Time todo
    # TODO: Need to add a setting for working days so we know if today has any hours to be done
    todo_today = _settings.hours_per_day * 60 * 60
    todo_this_week = (_settings.hours_per_day * 60 * 60) * _settings.days_per_week

    # Time remaining
    remaining_today = todo_today - logged_today
    remaining_this_week = todo_this_week - logged_this_week

    # Overtime (all time)
    # This is a little inefficient as it must go through all records
    overtime = 0
    if first_record := Time.select().order_by(Time.start).first():
        from app.lib.util.date import calculate_expected_hours

        first_day = arrow.get(first_record.start).to(_tz)
        expected_hours = calculate_expected_hours(
            start=first_day,
            end=today,
            hours_per_day=_settings.hours_per_day,
        )

        overtime = -(expected_hours * 60 * 60)  # Convert to seconds

        if total_logged := sum([rec.logged() for rec in Time.select()]):
            overtime += total_logged

    return TimeStats(
        logged_this_week=humanize_seconds(logged_this_week, short=True),
        logged_today=humanize_seconds(logged_today, short=True),
        remaining_this_week=humanize_seconds(remaining_this_week, short=True),
        remaining_today=humanize_seconds(remaining_today, short=True),
        overtime=humanize_seconds(overtime, short=True),
    )
