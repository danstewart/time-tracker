import arrow


def humanize_seconds(seconds: int):
    base = arrow.utcnow()
    end = base.shift(seconds=seconds)
    return base.humanize(end, only_distance=True, granularity=["hour", "minute"])


def calculate_expected_hours(start: arrow.Arrow, end: arrow.Arrow, hours_per_day: float) -> int:
    """
    Calculates the expected work hours between two dates
    Assumes the work week is 5 days Mon-Fri

    Will adjust both dates to be Mondays, calculated the total weekends, remove them then remove the adjustment
    """
    work_days = (end - start).days + 1

    if not work_days:
        return 0

    import sys

    start_adjust = 0
    if start.weekday() > 0:
        start_adjust = start.weekday()

    end_adjust = 0
    if end.weekday() > 0:
        end_adjust = 7 - end.weekday()

    print(f'work_days = {work_days}', file=sys.stderr)
    print(f'start_adjust = {start_adjust}', file=sys.stderr)
    print(f'end_adjust = {end_adjust}', file=sys.stderr)

    work_days += start_adjust
    work_days += end_adjust

    weeks = work_days / 7
    weekends = weeks * 2

    work_days -= weekends

    work_days -= start_adjust
    work_days -= end_adjust

    if end_adjust:
        work_days += 2

    expected_hours = work_days * hours_per_day
    overtime = expected_hours

    print('---', file=sys.stderr)

    print(f'work_days = {work_days}', file=sys.stderr)
    print(f'weeks = {weeks}', file=sys.stderr)
    print(f'weekends = {weekends}', file=sys.stderr)
    print(f'expected_hours = {expected_hours}', file=sys.stderr)

    return overtime

