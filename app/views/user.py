from flask import Blueprint, flash, redirect, render_template, request
from flask import session as flask_session

from app.controllers.user.util import is_logged_in

v = Blueprint("user", __name__)


@v.get("/login")
def show_login_form():
    """
    Renders the login form
    The same form is used to register new users as well as trigger a password reset email
    If the user is already logged in then we redirect to the dashboard
    """
    if is_logged_in():
        return redirect("/")
    return render_template("pages/login.html.j2")


@v.post("/login")
def handle_login():
    """
    Handle the various login actions
    - login
    - register
    - password reset
    """
    from app.controllers.user import login, register, send_password_reset
    from app.controllers.user.exceptions import (
        UserAlreadyExistsError,
        UserAuthFailed,
        UserNotVerifiedError,
    )

    action = request.form["action"]
    email = request.form["email"]
    password = request.form["password"]

    match [action, email, password]:
        case ["login", email, password]:
            try:
                login_session = login(email, password)
                flask_session["login_session_key"] = login_session.key
                return redirect("/")
            except UserAuthFailed:
                flash("Invalid username or password.", "danger")
                return redirect("/login")
            except UserNotVerifiedError:
                flash("Check your inbox to continue.", "info")
                return redirect("/login")

        case ["register", email, password]:
            # The register flow will email the user a verification link
            # If the account already exists then we send an email notifying the user and prompt them
            # to reset their password
            from contextlib import suppress

            with suppress(UserAlreadyExistsError):
                register(email, password)

            flash("Check your inbox to continue.", "info")
            return redirect("/login")

        case ["forgot-password", email, _]:
            send_password_reset(email)

            flash(
                "If an account exists, you will receive an email with instructions on how to reset your password.",
                "info",
            )

            return redirect("/login")

    flash("Something went wrong, sorry.", "danger")
    return redirect("/login")


@v.get("/logout")
def logout():
    if "login_session_key" in flask_session:
        flask_session.pop("login_session_key")
    return redirect("/login")


@v.get("/verify/<token>")
def verify_user_email(token: str):
    """
    Verifies a user account
    """
    from app.controllers.user.token import parse_token
    from app.models import User

    payload = parse_token(token)
    if not payload:
        flash("Invalid token", "danger")
        return redirect("/login")

    user = User.get(id=payload["user_id"])
    if not user:
        flash("Invalid token", "danger")
        return redirect("/login")

    user.verify()

    flash("Your email has been verified.", "success")
    return redirect("/login")


@v.get("/password-reset/<token>")
def password_reset_form(token: str):
    return render_template("pages/password-reset.html.j2")


@v.post("/password-reset/<token>")
def password_reset_handler(token):
    from app.controllers.user.token import parse_token
    from app.models import User

    payload = parse_token(token)
    if not payload:
        flash("Invalid token", "danger")
        return redirect("/login")

    user = User.get(id=payload["user_id"])
    if not user:
        flash("Invalid token", "danger")
        return redirect("/login")

    user.verify()
    user.set_password(request.form["password"])

    flash("Password successfully updated.", "success")
    return redirect("/login")
