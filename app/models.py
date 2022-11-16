from typing import Optional

import arrow
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app import db


class User(db.Model):  # type:ignore
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(255), unique=True, nullable=False)
    password: Optional[str] = db.Column(db.String(255), nullable=True)
    verified: Optional[bool] = db.Column(db.Boolean, default=False, nullable=False)

    # settings = db.relationship("Settings", backref="user", uselist=False)
    # time_entries = db.relationship("Time", backref="user", lazy=True)
    # login_session = db.relationship("LoginSession", backref="user", lazy=True)

    def verify(self):
        """
        Sets `user.verified` to True and commits
        """
        self.verified = True
        db.session.commit()

    def set_password(self, password: str) -> "User":
        """
        Update the given users password
        """
        self.password = PasswordHasher().hash(password)
        db.session.commit()
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


class LoginSession(db.Model):  # type:ignore
    id: int = db.Column(db.Integer, primary_key=True)

    # Unique session ID, stored in user cookies
    key: str = db.Column(db.String(255), unique=True, nullable=False)

    # Unix timestamp
    expires: int = db.Column(db.Integer, nullable=False)

    user: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Time(db.Model):  # type:ignore
    id: int = db.Column(db.Integer, primary_key=True)
    start: int = db.Column(db.Integer, nullable=False)
    end: Optional[int] = db.Column(db.Integer, nullable=True)
    note: Optional[str] = db.Column(db.String(255), nullable=True)
    user: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    breaks: list["Break"] = db.relationship("Break", lazy=True)

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
        from app.controllers.user.util import get_user

        user = get_user()
        return Time.query.filter(Time.start >= timestamp, Time.user == user).all()


class Break(db.Model):  # type:ignore
    id = db.Column(db.Integer, primary_key=True)
    time: int = db.Column(db.Integer, db.ForeignKey("time.id"))
    start: int = db.Column(db.Integer, primary_key=True)
    end: Optional[int] = db.Column(db.Integer, nullable=True)
    note: Optional[str] = db.Column(db.Integer, nullable=True)


class Settings(db.Model):  # type:ignore
    id: int = db.Column(db.Integer, primary_key=True)
    timezone: str = db.Column(db.String(255), nullable=False)
    # 1 = Monday, 7 = Sunday
    week_start: int = db.Column(db.Integer, nullable=False)
    hours_per_day: float = db.Column(db.Float, nullable=False)
    work_days: str = db.Column(
        db.String(7), nullable=False
    )  # This is stored as a 7 char string, the day char if the day is a work day and a hyphen if not, eg: MTWTF--

    user: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def work_days_list(self) -> list[str]:
        work_days = []
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day, day_name in zip(self.work_days, day_names):
            if day != "-":
                work_days.append(day_name)
        return work_days

    def total_work_days(self):
        return sum([1 if day != "-" else 0 for day in self.work_days])
