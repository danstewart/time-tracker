from functools import wraps

from flask import flash, redirect
from flask import session as flask_session

from app.controllers.user.exceptions import UserNotLoggedIn
from app.models import LoginSession, User


def get_user() -> User:
    """
    Fetch the user ID from the login session and return the User
    """
    import arrow

    if login_session_key := flask_session.get("login_session_key"):
        if login_session := LoginSession.get(key=login_session_key):
            if login_session.expires < arrow.utcnow().int_timestamp:
                flask_session.pop("login_session_key")
            else:
                return login_session.user
    raise UserNotLoggedIn()


def is_logged_in() -> bool:
    """Returns True if the user is logged in"""
    from contextlib import suppress

    with suppress(UserNotLoggedIn):
        get_user()
        return True
    return False


def login_required(f):
    """
    View decorator that will ensures user is logged in
    If not they are redirected to the login form and a flash message is shown
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if is_logged_in():
            return f(*args, **kwargs)
        else:
            flash("You need to login first.", "warning")
            return redirect("/login")

    return decorated
