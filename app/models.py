from typing import Optional

import arrow
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.lib.database import db, pony


class User(db.Entity):  # type:ignore
    id: int = pony.PrimaryKey(int, auto=True)  # type:ignore
    email: str = pony.Required(str, unique=True)  # type:ignore
    password: Optional[str] = pony.Optional(str)  # type:ignore
    verified: Optional[bool] = pony.Optional(bool, default=False)  # type:ignore

    settings: Optional["Settings"] = pony.Optional("Settings")  # type:ignore
    time_entries: list["Time"] = pony.Set("Time")  # type:ignore

    login_session: list["LoginSession"] = pony.Set("LoginSession")  # type:ignore

    def verify(self):
        """
        Sets `user.verified` to True and commits
        """
        self.verified = True
        pony.commit()

    def set_password(self, password: str) -> "User":
        """
        Update the given users password
        """
        self.password = PasswordHasher().hash(password)
        pony.commit()
        return self

    def check_password(self, password: str) -> bool:
        """
        Check if the provided password is correct for a given account
        """
        if not self.password:
            return False

        try:
            PasswordHasher().verify(self.password, password)
        except VerifyMismatchError:
            return False
        return True


class LoginSession(db.Entity):  # type:ignore
    id: int = pony.PrimaryKey(int, auto=True)  # type:ignore

    # Unique session ID, stored in user cookies
    key: str = pony.Required(str, unique=True)  # type:ignore

    # Unix timestamp
    expires: int = pony.Required(int)  # type:ignore

    user = pony.Required(User)


class Time(db.Entity):  # type:ignore
    id: int = pony.PrimaryKey(int, auto=True)  # type:ignore
    start: int = pony.Required(int)  # type:ignore
    end: Optional[int] = pony.Optional(int)  # type:ignore
    note: Optional[str] = pony.Optional(str)  # type:ignore

    breaks: list["Break"] = pony.Set("Break")  # type:ignore
    user: User = pony.Required(User)  # type:ignore

    def logged(self):
        """
        Return the total duration of a time entry in seconds
        With any breaks removed
        """
        now = arrow.utcnow().int_timestamp
        to_remove = sum([(_break.end or now) - _break.start for _break in self.breaks])
        end = self.end or now
        duration = end - self.start

        return duration - to_remove

    @classmethod
    def since(cls, timestamp):
        return pony.select(row for row in cls if row.start >= timestamp)


class Break(db.Entity):  # type:ignore
    time: Time = pony.Required(Time)  # type:ignore
    start: int = pony.Required(int)  # type:ignore
    end: Optional[int] = pony.Optional(int)  # type:ignore
    note: Optional[str] = pony.Optional(str)  # type:ignore


class Settings(db.Entity):  # type:ignore
    id: int = pony.PrimaryKey(int, auto=True)  # type:ignore
    timezone: str = pony.Required(str)  # type:ignore
    week_start: int = pony.Required(int)  # type:ignore
    hours_per_day: float = pony.Required(float)  # type:ignore
    work_days: str = pony.Required(  # type:ignore
        str
    )  # This is stored as a 7 char string, the day char if the day is a work day and a hyphen if not, eg: MTWTF--

    user: User = pony.Required(User)  # type:ignore

    def work_days_list(self) -> list[str]:
        work_days = []
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day, day_name in zip(self.work_days, day_names):
            if day != "-":
                work_days.append(day_name)
        return work_days

    def total_work_days(self):
        return sum([1 if day != "-" else 0 for day in self.work_days])
