import arrow


def humanize_seconds(seconds: int):
    base = arrow.utcnow()
    end = base.shift(seconds=seconds)
    return base.humanize(end, only_distance=True, granularity=["hour", "minute"])
