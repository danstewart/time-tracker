from typing import Optional

import arrow
from flask import abort

from app import db
from app.controllers import settings
from app.controllers.user.util import get_user
from app.models import Leave


def get(row_id: int) -> Leave:
    return Leave.query.filter(Leave.id == row_id).one()


def create(leave_type: str, start: int, duration: float, note: str = "") -> Leave:
    _settings = settings.fetch()
    _tz = _settings.timezone
    start_dt = arrow.get(start, tzinfo=_tz).int_timestamp

    leave = Leave(
        leave_type=leave_type,
        start=start_dt,
        duration=duration,
        note=note,
        user_id=get_user().id,
    )
    db.session.add(leave)
    db.session.commit()

    return leave


def update(row_id: int, leave_type: str, start: int, duration: float, note: Optional[str] = None) -> Leave:
    leave = db.session.scalars(db.select(Leave).where(Leave.id == row_id)).first()
    if not leave:
        abort(403)

    _settings = settings.fetch()
    _tz = _settings.timezone
    start_dt = arrow.get(start, tzinfo=_tz).int_timestamp

    leave.leave_type = leave_type
    leave.start = start_dt
    leave.duration = duration
    leave.note = note
    db.session.commit()

    return leave


def all_for_week(week: Optional[str] = None) -> list[Leave]:
    """
    Return all leave records sorted by start date for the given week

    Week should be in the format ${YEAR}-W${WEEK_NUMBER}, eg 2022-W25
    """

    # TODO: A lot of duplicated logic between this and `time.all_for_week()`
    _settings = settings.fetch()
    _tz = _settings.timezone

    local_now = arrow.now(tz=_tz)

    if not week:
        now = arrow.utcnow()
        week = "{}-W{}".format(now.year, now.week)

    week_start = arrow.get(week)

    # Adjust for `settings.week_start`
    if _settings.week_start_0 > 0:
        week_start = week_start.shift(weekday=_settings.week_start_0)

        if _settings.week_start_0 > local_now.weekday():
            week_start = week_start.shift(weeks=-1)

    week_end = week_start.shift(days=7)

    return (
        Leave.query.filter(
            Leave.user == get_user(),
            Leave.start >= week_start.int_timestamp,
            Leave.start < week_end.int_timestamp,
        )
        .order_by(Leave.start.desc(), Leave.id.desc())
        .all()
    )
