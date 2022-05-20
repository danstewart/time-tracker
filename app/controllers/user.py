from functools import wraps

from app.lib.database import pony
from app.lib.redis import session
from app.models import User
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import flash, redirect


class UserNotLoggedIn(Exception):
    ...

class UserAlreadyExistsError(Exception):
    ...


class UserAuthFailed(Exception):
    ...


class UserNotVerifiedError(Exception):
    ...


def register(email: str, password: str) -> User:
    """
    Registers and returns a new user
    If the email is already in use, a UserAlreadyExistsError is raised
    """
    user = User.get(email=email)

    if user:
        # TODO: Send email to user
        raise UserAlreadyExistsError(email)

    password = PasswordHasher().hash(password)

    # TODO: Send verification email to user
    new_user = User(email=email, password=password)
    pony.commit()

    return new_user


def login(email: str, password: str) -> User:
    """
    Authenticates and returns a user
    If the user cannot be authenticated a UserAuthFailed is raised
    If the user has not verified their email a UserNotVerifiedError is raised
    """
    user = User.get(email=email)

    if not user:
        raise UserAuthFailed("User not found")

    try:
        PasswordHasher().verify(user.password, password)
    except VerifyMismatchError:
        raise UserAuthFailed("Password mismatch")

    if not user.verified:
        raise UserNotVerifiedError("User not verified")

    return user


def send_password_reset(email: str):
    # TODO
    ...


def get_user() -> User:
    """
    Fetch the user ID from the session and return the user
    """
    if user_id := session.get("login"):
        return User.get(id=int(user_id))
    raise UserNotLoggedIn()

def is_logged_in() -> bool:
    """Returns True if the user is logged in"""
    if session.get("login"):
        return True
    return False


def login_required(f):
    """
    View decorator that will ensures user is logged in
    If not they are redirected to the login form and a flash message is shown
    """

    @wraps(f)
    def decorated(*args, **kwargs):

        if session.get("login"):
            return f(*args, **kwargs)
        else:
            flash("You need to login first.", "warning")
            return redirect("/login")

    return decorated
