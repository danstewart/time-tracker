from flask import current_app as app
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
            subject="Welcome to LogMyTime",
            html=render_template(
                "email/account_exists.html.j2",
                password_reset_url=f"{app.config['HOST']}/password-reset/{reset_token}",
            ),
        )
        raise UserAlreadyExistsError(email)

    # Otherwise create the new user
    new_user = User(email=email).set_password(password)
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
        subject="Welcome to LogMyTime",
        html=render_template(
            "email/welcome.html.j2",
            verify_url=f"{app.config['HOST']}/verify/{verify_token}",
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

    from app.lib.util.security import generate_csrf_token

    user = User.get(email=email)

    if not user:
        raise UserAuthFailed("User not found")

    if not user.verified:
        raise UserNotVerifiedError("User not verified")

    ok = user.check_password(password)
    if not ok:
        raise UserAuthFailed("Password mismatch")

    # Generate a new CSRF token for this session
    generate_csrf_token(user.id)

    # Log in
    return LoginSession(
        key=secrets.token_hex(),
        expires=arrow.utcnow().shift(hours=7 * 24).int_timestamp,
        user=user,
    )


def logout():
    from flask import session as flask_session

    if login_session_key := flask_session.get("login_session_key"):
        if login_session := LoginSession.get(key=login_session_key):
            login_session.delete()
        flask_session.pop("login_session_key")


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

        send_email(
            to_email=user.email,
            subject="LogMyTime: Password Reset",
            html=render_template(
                "email/password_reset.html.j2",
                password_reset_url=f"{app.config['HOST']}/password-reset/{reset_token}",
            ),
        )


def update_email(user: User, new_email: str):
    """
    Sends a user a verification email to verify their new email address
    If not clicked then nothing is changed
    """

    # If an account already exists for this email then send a different email advising the user to use the existing account
    if existing_user := User.get(email=new_email):
        reset_token = create_token(
            {
                "type": "password-reset",
                "user_id": existing_user.id,
            }
        )
        send_email(
            to_email=new_email,
            subject="Email change for LogMyTime",
            html=render_template(
                "email/email_change_already_exists.html.j2",
                password_reset_url=f"{app.config['HOST']}/password-reset/{reset_token}",
            ),
        )
        return

    verify_token = create_token(
        payload={
            "type": "verify",
            "user_id": user.id,
            "new_email": new_email,
        },
        timeout=604800,  # 7 days
    )

    send_email(
        to_email=new_email,
        subject="Email change for LogMyTime",
        html=render_template(
            "email/email_change.html.j2",
            verify_url=f"{app.config['HOST']}/verify/{verify_token}",
        ),
    )


def delete_account(user: User):
    """
    Deletes a user's account
    """
    from app.models import User

    # We have cascading deletes :)
    User.get(id=user.id).delete()

    pony.commit()


def export_data(user: User) -> str:
    import json

    from app.controllers import settings, time

    time_records = []
    for time in time.all():
        rec = time.to_dict(exclude=["id", "user"])
        rec["breaks"] = []
        for brk in time.breaks:
            rec["breaks"].append(brk.to_dict(exclude=["id", "time"]))

        time_records.append(rec)

    export = {
        "time": time_records,
        "settings": settings.fetch().to_dict(exclude=["id", "user"]),
        "user": user.to_dict(exclude=["id", "password", "settings"]),
    }

    return json.dumps(export)
