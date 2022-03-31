import arrow


def humanize_seconds(seconds: int, short: bool = False):
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


def calculate_expected_hours(start: arrow.Arrow, end: arrow.Arrow, hours_per_day: float) -> int:
    """
    Calculates the expected work hours between two dates
    Assumes the work week is 5 days Mon-Fri

    Date range is inclusive of both the start and end

    Will adjust both dates to be Mondays, calculated the total weekends, remove them then remove the adjustment
    """
    # TODO:
    # - This can probably be simplified
    # - Figure out how to support different work days - good luck...

    # Adjust our dates to be midnight
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end.replace(hour=0, minute=0, second=0, microsecond=0)

    work_days = (end - start).days

    if work_days < 0:
        return 0

    # Special case for handling 1 day
    if work_days == 0:
        return hours_per_day if start.weekday() < 5 else 0

    # Special case for weekend only
    if work_days < 6 and start.weekday() >= 5 and end.weekday() >= 5:
        return 0

    # If we are spanning over a week then adjust the counter
    # to count from Monday to Monday
    # This makes the weekend calculation easier
    # We push both dates back to their previous Mondays
    start_adjust, end_adjust = 0, 0

    if work_days >= 6:
        if start.weekday() > 0:
            start_adjust = start.weekday()

        if end.weekday() > 0:
            end_adjust = end.weekday()

        # Add out Monday adjustments
        work_days += start_adjust
        work_days -= end_adjust

        # Work out how many weekend days there are
        weeks = work_days / 7
        weekends = weeks * 2

        # Take off the weekends
        work_days -= weekends

    # If we start or end on a weekend then adjust to ignore those days
    if start.weekday() >= 5:
        work_days += 7 - start.weekday()

    if end.weekday() >= 5:
        work_days -= end.weekday() - 4

    # Take off our Monday adjustments
    work_days -= start_adjust
    work_days += end_adjust

    # Calculate the expected hours
    # Add 1 here to include the start day
    work_days += 1
    expected_hours = work_days * hours_per_day
    overtime = expected_hours

    return overtime
