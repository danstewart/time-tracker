from typing import Optional

import arrow
from flask import abort

from app import db
from app.controllers import settings
from app.controllers.user.util import get_user
from app.lib.logger import get_logger
from app.models import Break, Time

logger = get_logger(__name__)


def get(row_id: str) -> Time:
    t = db.session.scalars(db.select(Time).filter(Time.id == row_id, Time.user == get_user())).first()
    if not t:
        abort(403)
    return t


def all() -> list[Time]:
    """Return all time records sorted by start date"""
    return (
        Time.query.filter(
            Time.user == get_user(),
        )
        .order_by(Time.start.desc(), Time.id.desc())
        .all()
    )


def current() -> Optional[Time]:
    """
    Return the current clocked in time record (if there is one)
    """
    return db.session.scalars(
        db.select(Time)
        .filter(
            Time.user == get_user(),
            Time.end == None,
        )
        .order_by(Time.start.desc())
    ).first()


def current_break() -> Optional[Break]:
    """
    Return the current clocked in break record (if there is one)
    """
    return db.session.scalars(
        db.select(Break)
        .filter(
            Break.time.has(user=get_user()),
            Break.end == None,
        )
        .order_by(Break.start.desc())
    ).first()


def all_for_week(week: Optional[str] = None) -> list[Time]:
    """
    Return all time records sorted by start date for the given week

    Week should be in the format ${YEAR}-W${WEEK_NUMBER}, eg 2022-W25
    """
    _settings = settings.fetch()
    _tz = _settings.timezone

    local_now = arrow.now(tz=_tz)

    if not week:
        now = arrow.utcnow()

        y, w = now.year, now.week

        # Handle the case where the new year starts but the week started the previous year
        if w >= 52 and now.month == 1:
            y -= 1

        week = "{}-W{:02}".format(y, w)

    week_start = arrow.get(week)

    # Adjust for `settings.week_start`
    if _settings.week_start_0 > 0:
        week_start = week_start.shift(weekday=_settings.week_start_0)

        if _settings.week_start_0 > local_now.weekday():
            week_start = week_start.shift(weeks=-1)

    week_end = week_start.shift(days=7)
    return (
        Time.query.filter(
            Time.user == get_user(),
            Time.start >= week_start.int_timestamp,
            Time.start < week_end.int_timestamp,
        )
        .order_by(Time.start.desc(), Time.id.desc())
        .all()
    )


def create(start: str, end: Optional[str] = None, note: str = "") -> Time:
    """Create a new time record"""
    _settings = settings.fetch()
    _tz = _settings.timezone

    start_dt = arrow.get(start, tzinfo=_tz).int_timestamp

    end_dt = None
    if end:
        end_dt = arrow.get(end, tzinfo=_tz).int_timestamp

    new_record = Time(
        start=start_dt,
        end=end_dt,
        note=note,
        user_id=get_user().id,
    )

    db.session.add(new_record)
    db.session.commit()
    return new_record


def update(row_id: str, start: str, end: Optional[str] = None, note: str = "") -> Time:
    _settings = settings.fetch()
    _tz = _settings.timezone

    start_dt = arrow.get(start, tzinfo=_tz).int_timestamp

    end_dt = None
    if end:
        end_dt = arrow.get(end, tzinfo=_tz).int_timestamp

    t = db.session.scalars(db.select(Time).filter(Time.id == row_id, Time.user == get_user())).first()
    if not t:
        abort(403)

    t.start = start_dt
    t.end = end_dt
    t.note = note

    db.session.commit()
    return t


def delete(row_id: int) -> bool:
    """
    Deletes a time record by ID
    Returns True if deleted and False if not
    """
    if record := db.session.scalars(db.select(Time).filter(Time.id == row_id, Time.user == get_user())).first():
        db.session.delete(record)
        db.session.commit()
        return True
    return False


def clock_out(end: str):
    """Sets the end time for the current time record"""
    _settings = settings.fetch()
    _tz = _settings.timezone

    end_dt = arrow.get(end, tzinfo=_tz)

    current_record = db.session.scalars(
        db.select(Time)
        .filter(
            Time.user == get_user(),
            Time.end == None,
        )
        .order_by(Time.start.desc())
    ).first()

    if current_record:
        current_record.end = end_dt.int_timestamp
        current_record.logged = end_dt.int_timestamp - current_record.start
        db.session.commit()


def break_start(start: str):
    """Sets the start time for the current time record"""
    _settings = settings.fetch()
    _tz = _settings.timezone

    start_dt = arrow.get(start, tzinfo=_tz)

    current_record = db.session.scalars(
        db.select(Time)
        .filter(
            Time.user == get_user(),
            Time.end == None,
        )
        .order_by(Time.start.desc())
    ).first()

    if not current_record:
        return

    db.session.add(
        Break(
            time_id=current_record.id,
            start=start_dt.int_timestamp,
        )
    )

    db.session.commit()


def break_end(end: str):
    """Sets the start time for the current time record"""
    _settings = settings.fetch()
    _tz = _settings.timezone

    end_dt = arrow.get(end, tzinfo=_tz)

    current_record = db.session.scalars(
        db.select(Time)
        .filter(
            Time.user == get_user(),
            Time.end == None,
        )
        .order_by(Time.start.desc())
    ).first()

    if not current_record:
        return

    current_break = db.session.scalars(
        db.select(Break).filter(
            Break.time_id == current_record.id,
            Break.end == None,
        )
    )

    if brk := current_break.first():
        brk.end = end_dt.int_timestamp

    db.session.commit()


def add_break(time_id: str, break_start: str, break_end: str | None):
    time_record = db.session.scalars(db.select(Time).filter(Time.id == time_id, Time.user == get_user())).first()
    if not time_record:
        abort(403)

    _settings = settings.fetch()
    _tz = _settings.timezone

    start_dt = arrow.get(break_start, tzinfo=_tz)
    end_dt = arrow.get(break_end, tzinfo=_tz) if break_end else None

    db.session.add(
        Break(
            time_id=time_record.id,
            start=start_dt.int_timestamp,
            end=end_dt.int_timestamp if end_dt else None,
        )
    )

    db.session.commit()


def bulk_update(table, data: dict[int, dict]):
    """
    Updates multiple time records at once

    `table`: "time" or "break"
    `data`: A dict of {row_id: {column1: value1, column2: value2}}
    """
    _settings = settings.fetch()
    _tz = _settings.timezone

    model = Time if table == "time" else Break

    for row_id, values in data.items():
        row = db.session.scalars(db.select(model).filter_by(id=row_id)).one()
        for key, value in values.items():
            # Convert string dates to int timestamps
            if key in ("start", "end") and value:
                value = arrow.get(value, tzinfo=_tz).int_timestamp
            setattr(row, key, value if value else None)

    db.session.commit()
