from dataclasses import dataclass


@dataclass
class TimeStats:
    logged_this_week: str
    logged_today: str
    remaining_this_week: str
    remaining_today: str
    overtime: str
