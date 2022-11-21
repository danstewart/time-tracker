from typing import Optional

import arrow
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app import db


class BaseModel(db.Model):  # type: ignore
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def update(self, **kwargs):
        """
        This function allows calling Model.update(field1=val1, field2=val2, ...)
        The main purpose of this is compatability with VersionAlchemy as Session.execute(update())
        skips the ORM and VersionAlchemy
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def asdict(self, exclude: list | None = None):
        result = {}
        for field in self.fields():
            if exclude and field in exclude:
                continue
            result[field] = getattr(self, field)
        return result

    @classmethod
    def fields(cls):
        """
        Return a list of the columns
        """
        return [col.name for col in cls.__table__.columns]


class User(BaseModel):
    email: str = db.Column(db.String(255), unique=True, nullable=False)
    password: Optional[str] = db.Column(db.String(255), nullable=True)
    verified: Optional[bool] = db.Column(db.Boolean, default=False, nullable=False)

    sessions = db.relationship("LoginSession", backref="user", cascade="all, delete-orphan")
    settings = db.relationship("Settings", backref="user", cascade="all, delete-orphan")

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


class LoginSession(BaseModel):
    # Unique session ID, stored in user cookies
    key: str = db.Column(db.String(255), unique=True, nullable=False)

    # Unix timestamp
    expires: int = db.Column(db.Integer, nullable=False)

    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Time(BaseModel):
    start: int = db.Column(db.Integer, nullable=False)
    end: Optional[int] = db.Column(db.Integer, nullable=True)
    note: Optional[str] = db.Column(db.String(255), nullable=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    breaks: list["Break"] = db.relationship("Break", lazy=True, backref="time", cascade="all, delete-orphan")
    user: User = db.relationship("User", viewonly=True)

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
        return db.session.scalars(db.select(Time).filter(Time.start >= timestamp, Time.user == user)).all()


class Break(BaseModel):
    time_id: int = db.Column(db.Integer, db.ForeignKey("time.id"))
    start: int = db.Column(db.Integer)
    end: Optional[int] = db.Column(db.Integer, nullable=True)
    note: Optional[str] = db.Column(db.String(255), nullable=True)


class Leave(BaseModel):
    leave_type: str = db.Column(db.String(255), nullable=False)  # sick / annual
    start: int = db.Column(db.Integer, nullable=False)  # unix time for starting day
    duration: float = db.Column(db.Float, nullable=False)  # Duration in days
    note: Optional[str] = db.Column(db.String(255), nullable=True)


class Settings(BaseModel):
    timezone: str = db.Column(db.String(255), nullable=False)
    # 1 = Monday, 7 = Sunday
    week_start: int = db.Column(db.Integer, nullable=False)
    hours_per_day: float = db.Column(db.Float, nullable=False)
    work_days: str = db.Column(
        db.String(7), nullable=False
    )  # This is stored as a 7 char string, the day char if the day is a work day and a hyphen if not, eg: MTWTF--

    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    @property
    def week_start_0(self):
        return self.week_start - 1

    def work_days_list(self) -> list[str]:
        work_days = []
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day, day_name in zip(self.work_days, day_names):
            if day != "-":
                work_days.append(day_name)
        return work_days

    def total_work_days(self):
        return sum([1 if day != "-" else 0 for day in self.work_days])
