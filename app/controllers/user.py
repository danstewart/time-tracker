from functools import wraps

from app.models import User
from flask import flash, redirect, session


def is_logged_in() -> bool:
    return "user" in session


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if "login" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first.", "warning")
            return redirect("/login")

    return decorated


def get_user() -> User:
    user_id = session["login"]
    return User.get(id=user_id)
