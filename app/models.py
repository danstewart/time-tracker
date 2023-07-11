from typing import NewType, Optional

import arrow
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db

UnixTimestamp = NewType("UnixTimestamp", int)
DurationDays = NewType("DurationDays", float)


class BaseModel(db.Model):  # type: ignore
    __abstract__ = True

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)

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
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    password: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)
    verified: Mapped[Optional[bool]] = mapped_column(db.Boolean, default=False, nullable=False)
    last_seen_whats_new: Mapped[Optional[int]] = mapped_column(db.Integer, db.ForeignKey("whats_new.id"), nullable=True)
    is_admin: Mapped[Optional[bool]] = mapped_column(db.Boolean)

    sessions: Mapped[list["LoginSession"]] = relationship("LoginSession", backref="user", cascade="all, delete-orphan")
    settings: Mapped["Settings"] = relationship(backref="user", cascade="all, delete-orphan", uselist=False)

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
    key: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    expires: Mapped[UnixTimestamp] = mapped_column(db.Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Time(BaseModel):
    start: Mapped[UnixTimestamp] = mapped_column(db.Integer, nullable=False)
    end: Mapped[Optional[UnixTimestamp]] = mapped_column(db.Integer, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    breaks: Mapped[list["Break"]] = relationship("Break", lazy=True, backref="time", cascade="all, delete-orphan")
    user: Mapped[User] = relationship("User", viewonly=True)

    def logged(self):
        """
        Return the total duration of a time entry in seconds
        With any breaks removed
        """
        now = arrow.utcnow().int_timestamp
        to_remove = sum([(_break.end or now) - _break.start for _break in self.breaks], start=0)
        end = self.end or now
        duration = end - self.start

        return duration - to_remove

    @classmethod
    def since(cls, timestamp):
        from app.controllers.user.util import get_user

        user = get_user()
        return db.session.scalars(db.select(Time).filter(Time.start >= timestamp, Time.user == user)).all()


class Break(BaseModel):
    time_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("time.id"))
    start: Mapped[UnixTimestamp] = mapped_column(db.Integer)
    end: Mapped[Optional[UnixTimestamp]] = mapped_column(db.Integer, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)


class Leave(BaseModel):
    leave_type: Mapped[str] = mapped_column(db.String(255), nullable=False)  # sick / annual
    start: Mapped[UnixTimestamp] = mapped_column(db.Integer, nullable=False)
    duration: Mapped[DurationDays] = mapped_column(db.Float, nullable=False)
    public_holiday: Mapped[Optional[bool]] = mapped_column(db.Boolean, default=False)
    note: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user: Mapped[User] = relationship("User", viewonly=True)

    @classmethod
    def since(cls, timestamp):
        from app.controllers.user.util import get_user

        user = get_user()
        return db.session.scalars(db.select(Leave).filter(Leave.start >= timestamp, Leave.user == user)).all()

    def logged(self) -> int:
        """
        Returns the duration in seconds of this leave entry
        """
        hours_per_day = self.user.settings.hours_per_day
        return int(self.duration * hours_per_day * 60 * 60)


class Settings(BaseModel):
    timezone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    holiday_location: Mapped[str] = mapped_column(db.String(255), nullable=True)

    # 1 = Monday, 7 = Sunday
    week_start: Mapped[int] = mapped_column(db.Integer, nullable=False)
    hours_per_day: Mapped[float] = mapped_column(db.Float, nullable=False)
    work_days: Mapped[str] = mapped_column(
        db.String(7), nullable=False
    )  # This is stored as a 7 char string, the day char if the day is a work day and a hyphen if not, eg: MTWTF--

    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    @classmethod
    def default(cls, user_id: int):
        return cls(
            timezone="Europe/London",
            week_start=1,
            hours_per_day=7.5,
            work_days="MTWTF--",
            user_id=user_id,
        )

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


class WhatsNew(BaseModel):
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    created_at: Mapped[int] = mapped_column(db.Integer, nullable=False)
