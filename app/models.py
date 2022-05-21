import arrow

from app.lib.database import db, pony


class User(db.Entity):
    id = pony.PrimaryKey(int, auto=True)
    email = pony.Required(str, unique=True)
    password = pony.Required(str)
    locked = pony.Optional(bool, default=False)
    verified = pony.Optional(bool, default=True)

    settings = pony.Optional("Settings")
    time_entries = pony.Set("Time")

    login_session = pony.Set("LoginSession")

    def get_token(self, token_type: str, timeout: int = 3600, force_new: bool = False) -> str:
        """
        Returns a cryptographically secure token for the user and a specific token type

        First checks if the specified token type exists in the session
        If so it is returned, otherwise a new token is generated and stored in the session
        This is so it can be fetched back out for comparison later

        `token_type`
            The type of token, used to make the key in the session
        `timeout`
            The number of seconds the token is valid for
        `force_new`
            If True then a new token is always generated and stored in the session
            Overwriting and invalidating any existing token
        """
        import secrets

        from app.lib.redis import session

        token_key = "{}:token:{}".format(self.id, token_type)

        if not force_new:
            if token := session.get(token_key):
                return token.decode("utf-8")

        token = secrets.token_hex()
        session.set(token_key, token)
        session.expire(token_key, timeout)
        return token


class LoginSession(db.Entity):
    id = pony.PrimaryKey(int, auto=True)
    key = pony.Required(str, unique=True)  # Unique session ID, stored in user cookies
    expires = pony.Required(int)  # Unix timestamp

    user = pony.Required(User)


class Time(db.Entity):
    id = pony.PrimaryKey(int, auto=True)
    start = pony.Required(int)
    end = pony.Optional(int)
    note = pony.Optional(str)

    breaks = pony.Set("Break")
    user = pony.Required(User)

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


class Break(db.Entity):
    time = pony.Required(Time)
    start = pony.Required(int)
    end = pony.Optional(int)
    note = pony.Optional(str)


class Settings(db.Entity):
    id = pony.PrimaryKey(int, auto=True)
    timezone = pony.Required(str)
    week_start = pony.Required(int)
    hours_per_day = pony.Required(float)
    work_days = pony.Required(
        str
    )  # This is stored as a 7 char string, the day char if the day is a work day and a hyphen if not, eg: MTWTF--

    user = pony.Required(User)

    def work_days_list(self) -> list[str]:
        work_days = []
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day, day_name in zip(self.work_days, day_names):
            if day != "-":
                work_days.append(day_name)
        return work_days

    def total_work_days(self):
        return sum([1 if day != "-" else 0 for day in self.work_days])
