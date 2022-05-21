from functools import wraps

from app.lib.database import pony
from app.lib.email import send_email
from app.models import LoginSession, User
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import flash, redirect, render_template
from flask import session as flask_session


# fmt:off
class UserNotLoggedIn(Exception): ...
class UserAlreadyExistsError(Exception): ...
class UserAuthFailed(Exception): ...
class UserNotVerifiedError(Exception): ...
# fmt:on


def register(email: str, password: str) -> User:
    """
    Registers and returns a new user
    If the email is already in use, a UserAlreadyExistsError is raised
    """
    user = User.get(email=email)

    if user:
        reset_token = user.get_token("password-reset")
        send_email(
            to_email=email,
            subject="Welcome to Time Tracker",
            html=render_template(
                "email/account_exists.html.j2",
                password_reset_url=f"http://localhost:4000/password-reset/{reset_token}",
            ),
        )
        raise UserAlreadyExistsError(email)

    password = PasswordHasher().hash(password)

    new_user = User(email=email, password=password)
    pony.commit()

    verify_token = new_user.get_token("verify", timeout=604800)  # 7 days
    send_email(
        to_email=email,
        subject="Welcome to Time Tracker",
        html=render_template(
            "email/welcome.html.j2",
            verify_url=f"http://localhost:4000/verify/{verify_token}",
        ),
    )

    return new_user


def login(email: str, password: str) -> LoginSession:
    """
    Authenticates a user and returns a LoginSession
    If the user cannot be authenticated a UserAuthFailed is raised
    If the user has not verified their email a UserNotVerifiedError is raised
    """
    import secrets

    import arrow

    # TODO: Check if user is verified
    # do not allow login if not verified
    user = User.get(email=email)

    if not user:
        raise UserAuthFailed("User not found")

    try:
        PasswordHasher().verify(user.password, password)
    except VerifyMismatchError:
        raise UserAuthFailed("Password mismatch")

    if not user.verified:
        raise UserNotVerifiedError("User not verified")

    return LoginSession(
        key=secrets.token_hex(),
        expires=arrow.utcnow().shift(hours=7 * 24).int_timestamp,
        user=user,
    )


def send_password_reset(email: str):
    """
    If an email exists in the system then send a password reset email
    """
    if user := User.get(email=email):
        reset_token = user.get_token("password-reset")
        # TODO: Auto verify email if not already done
        send_email(
            to_email=user.email,
            subject="Time Tracker: Password Reset",
            html=render_template(
                "email/password_reset.html.j2",
                password_reset_url=f"http://localhost:4000/password-reset/{reset_token}",
            ),
        )


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
