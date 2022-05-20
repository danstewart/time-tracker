from app.controllers.user import is_logged_in
from app.lib.redis import session
from flask import Blueprint, flash, redirect, render_template, request

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
    from app.controllers.user import (
        UserAlreadyExistsError,
        UserAuthFailed,
        UserNotVerifiedError,
        login,
        register,
        send_password_reset,
    )

    action = request.form["action"]
    email = request.form["email"]
    password = request.form["password"]

    match [action, email, password]:
        case ["login", email, password]:
            try:
                user = login(email, password)
                session.set("login", user.id)
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
    if session.get("login"):
        session.delete("login")
    return redirect("/login")
