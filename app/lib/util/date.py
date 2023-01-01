import arrow


def humanize_seconds(seconds: int | float, short: bool = False):
    """
    Humanizes a duration in seconds

    `seconds`: The number of seconds to humanize
    `short`: If true then format as a shorter string

    Default is to call out to `arrow.humanize` -> "6 hours and 15 minutes"
    Short mode displays as "6h 15m"

    Seconds are never shown
    """
    base = arrow.utcnow()
    end = base.shift(seconds=seconds)

    if short:
        sign = ""
        hours = 0
        minutes = 0

        if seconds < 0:
            sign = "-"
            seconds = abs(seconds)

        while seconds >= 60:
            seconds -= 60
            minutes += 1

        while minutes >= 60:
            minutes -= 60
            hours += 1

        return f"{sign}{hours}h {minutes}m"

    return base.humanize(end, only_distance=True, granularity=["hour", "minute"])


def calculate_expected_hours(start: arrow.Arrow, end: arrow.Arrow, hours_per_day: float, days_worked: str) -> float:
    """
    Calculates the expected work hours between two dates
    Date range is inclusive of both the start and end

    `start`: Arrow object of start date
    `end`: Arrow object of end date
    `hours_per_day`: The number of hours per day
    `days_worked`: A string of work days, e.g. "MTWTF--" with "-" for non-work days
    """
    # Adjust our dates to be midnight
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end.replace(hour=0, minute=0, second=0, microsecond=0)

    # Monday = 0, Sunday = 6
    working_days = [False] * 7
    for i, day in enumerate(days_worked):
        if day != "-":
            working_days[i] = True

    days_to_check = (end - start).days

    # No days, no time expected
    if days_to_check < 0:
        return 0

    # If a single day check it's a work day, else 0 hours expected
    if days_to_check == 0:
        return hours_per_day if working_days[start.weekday()] else 0

    # Count the number of work days between the two dates
    work_days = 0
    while start <= end:
        if working_days[start.weekday()]:
            work_days += 1
        start = start.shift(days=1)

    # Calculate the expected hours
    expected_hours = work_days * hours_per_day

    return expected_hours
