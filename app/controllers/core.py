import arrow

from app import db
from app.controllers import settings
from app.controllers.user.util import get_user
from app.models import Leave, Time
from app.viewmodels import TimeStats


def _get_first_record_time() -> int | None:
    """
    Returns the timestamp of the first time or leave record
    """
    first_time = db.session.scalars(db.select(Time).filter(Time.user == get_user()).order_by(Time.start)).first()
    first_leave = db.session.scalars(db.select(Leave).filter(Leave.user == get_user()).order_by(Leave.start)).first()

    if not first_time and not first_leave:
        return None

    return min(map(lambda row: row.start, filter(lambda row: row is not None, [first_time, first_leave])))


def stats() -> TimeStats:
    """Return the weekly stats"""
    from app.lib.util.date import humanize_seconds

    _settings = settings.fetch()
    _tz = _settings.timezone

    now = arrow.now(tz=_tz)
    today = now.replace(hour=0, minute=0, second=0)

    if now.weekday() != _settings.week_start_0:
        start = today.shift(weekday=_settings.week_start_0).shift(days=-7)
    else:
        start = today

    # Time logged
    logged_today = sum([rec.logged() for rec in Time.since(today.int_timestamp)])
    leave_today = sum([rec.logged() for rec in Leave.since(today.int_timestamp)])

    logged_this_week = sum([rec.logged() for rec in Time.since(start.int_timestamp)])
    leave_this_week = sum([rec.logged() for rec in Leave.since(start.int_timestamp)])

    # Time to do
    current_day = now.format("dddd")
    work_days = _settings.work_days_list()
    total_work_days = _settings.total_work_days()

    todo_today = _settings.hours_per_day * 60 * 60 if current_day in work_days else 0
    todo_this_week = (_settings.hours_per_day * 60 * 60) * total_work_days

    # Time remaining
    remaining_today = todo_today - (logged_today + leave_today)
    remaining_this_week = todo_this_week - (logged_this_week + leave_this_week)

    # You can't have negative time remaining
    # Any extra time is displayed as overtime
    if remaining_today < 0:
        remaining_today = 0

    if remaining_this_week < 0:
        remaining_this_week = 0

    # Overtime (all time)
    # This is a little inefficient as it must go through all records
    overtime = 0

    if first_time := _get_first_record_time():
        from app.lib.util.date import calculate_expected_hours

        first_day = arrow.get(first_time).to(_tz)
        expected_hours = calculate_expected_hours(
            start=first_day,
            end=today,
            hours_per_day=_settings.hours_per_day,
        )

        overtime = -(expected_hours * 60 * 60)  # Convert to seconds

        total_logged = 0

        total_logged += sum(
            [rec.logged() for rec in db.session.scalars(db.select(Time).filter(Time.user == get_user())).all()]
        )

        total_logged += sum(
            [rec.logged() for rec in db.session.scalars(db.select(Leave).filter(Leave.user == get_user())).all()]
        )

        if total_logged:
            overtime += total_logged

    return TimeStats(
        logged_this_week=humanize_seconds(logged_this_week, short=True),
        logged_today=humanize_seconds(logged_today, short=True),
        remaining_this_week=humanize_seconds(remaining_this_week, short=True),
        remaining_today=humanize_seconds(remaining_today, short=True),
        overtime=humanize_seconds(overtime, short=True),
    )


def week_list() -> list[str]:
    """
    Returns a list of weeks since the first record in the format ${year}-W${week}, eg. 2022-W25
    """
    first_time = _get_first_record_time()
    if not first_time:
        return []

    first = arrow.get(first_time)
    now = arrow.utcnow()

    weeks = []
    while first < now:
        weeks.append("{}-W{}".format(first.year, first.week))
        first = first.shift(weeks=1)

    return list(reversed(weeks))
