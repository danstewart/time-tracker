from functools import wraps

import sqlalchemy as sa
from flask import flash, redirect
from flask import session as flask_session

from app import db
from app.controllers.user.exceptions import UserNotLoggedIn
from app.models import LoginSession, User


def get_user() -> User:
    """
    Fetch the user ID from the login session and return the User
    """
    import arrow

    if login_session_key := flask_session.get("login_session_key"):
        if login_session := db.session.scalars(sa.select(LoginSession).filter_by(key=login_session_key)).first():
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


def is_admin() -> bool:
    """Returns True if the user is an admin"""
    from contextlib import suppress

    with suppress(UserNotLoggedIn):
        u = get_user()
        return bool(u.is_admin)
    return False


def unseen_whats_new() -> int:
    """
    Return total unseen "What's New" messages
    """
    from contextlib import suppress

    from sqlalchemy import func

    from app.models import WhatsNew

    with suppress(UserNotLoggedIn):
        u = get_user()
        newest = db.session.query(WhatsNew).with_entities(func.max(WhatsNew.id)).scalar()

        # Nothing to show
        if not newest:
            return False

        # User has seen nothing
        if not u.last_seen_whats_new:
            return newest

        return newest - u.last_seen_whats_new
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


def admin_only(f):
    """
    View decorator that will ensures user is logged in and is an admin
    If not they are redirected to the login form and a flash message is shown
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if is_logged_in() and is_admin():
            return f(*args, **kwargs)
        else:
            flash("Permission denied.", "warning")
            return redirect("/dash")

    return decorated
