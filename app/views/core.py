from flask import Blueprint, flash, redirect, render_template, request, session

v = Blueprint("core", __name__)


@v.route("/login", methods=["GET", "POST"])
def login_form():
    from app.models import User, UserExistsError

    # TODO: Clean up
    if form := request.form:
        if "login" in form:
            user = User.authenticate(form.get("email", ""), form.get("password", ""))

            if user:
                session["login"] = user.id
                return redirect("/")
            else:
                flash("Invalid username or password.", "danger")

        elif "register" in form:
            user = None
            try:
                user = User.create(form.get("email", ""), form.get("password", ""))
            except UserExistsError:
                flash("User already exists.", "danger")

            if user:
                session["login"] = user.id
                flash("User created!", "success")
                return redirect("/")

        elif "forgot-password" in form:
            user = User.select(lambda row: row.email == form.get("email"))

            if user:
                user.send_password_reset_email()

            flash(
                "If an account exists with that email, you will receive an email with instructions on how to reset your password.",
                "info",
            )

    return render_template("pages/login.html.j2")


@v.get("/logout")
def logout():
    if "login" in session:
        session.pop("login")
    return redirect("/login")
