from functools import wraps

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import render_template

from app.controllers.user.exceptions import (
    UserAlreadyExistsError,
    UserAuthFailed,
    UserNotVerifiedError,
)
from app.controllers.user.token import create_token
from app.lib.database import pony
from app.lib.email import send_email
from app.models import LoginSession, User


def register(email: str, password: str) -> User:
    """
    Registers and returns a new user
    If the email is already in use, a UserAlreadyExistsError is raised
    """
    user = User.get(email=email)

    # If a user already exists with this email then send them a password reset link instead
    if user:
        reset_token = create_token(
            {
                "type": "password-reset",
                "user_id": user.id,
            }
        )
        send_email(
            to_email=email,
            subject="Welcome to Time Tracker",
            html=render_template(
                "email/account_exists.html.j2",
                password_reset_url=f"http://localhost:4000/password-reset/{reset_token}",
            ),
        )
        raise UserAlreadyExistsError(email)

    # Otherwise create the new user
    password = PasswordHasher().hash(password)
    new_user = User(email=email, password=password)
    pony.commit()

    verify_token = create_token(
        payload={
            "type": "verify",
            "user_id": new_user.id,
        },
        timeout=604800,  # 7 days
    )

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

    user = User.get(email=email)

    if not user:
        raise UserAuthFailed("User not found")

    if not user.verified:
        raise UserNotVerifiedError("User not verified")

    try:
        PasswordHasher().verify(user.password, password)
    except VerifyMismatchError:
        raise UserAuthFailed("Password mismatch")

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
        reset_token = create_token(
            {
                "type": "password-reset",
                "user_id": user.id,
            }
        )
        # TODO: Auto verify email if not already done
        send_email(
            to_email=user.email,
            subject="Time Tracker: Password Reset",
            html=render_template(
                "email/password_reset.html.j2",
                password_reset_url=f"http://localhost:4000/password-reset/{reset_token}",
            ),
        )
