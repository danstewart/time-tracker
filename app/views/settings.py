from flask import Blueprint, render_template, request

from app.controllers import settings
from app.controllers.user.util import login_required
from app.lib.logger import get_logger

v = Blueprint("settings", __name__)
logger = get_logger(__name__)


@v.route("/settings", methods=["GET", "POST"])
@v.route("/settings/general", methods=["GET", "POST"])
@login_required
def general_settings():
    if request.form:
        from flask import flash, redirect

        settings.update(**request.form)
        flash("Settings saved", "success")
        return redirect("/")

    return render_template("pages/settings.html.j2", settings=settings.fetch(), page="general")


@v.route("/settings/account", methods=["GET", "POST"])
@login_required
def account_settings():
    from app.controllers.user import update_email
    from app.controllers.user.util import get_user

    user = get_user()

    if request.form:
        from flask import flash, redirect

        has_changed = False
        submit = request.form.get("submit", "save")

        if submit == "delete-account":
            from app.controllers.user import delete_account, logout

            delete_account(user)
            logout()

            flash("Your account has been deleted", "success")
            return redirect("/login")
        elif submit == "export":
            from flask import make_response

            from app.controllers.user import export_data

            response = make_response(
                export_data(user),
            )
            response.headers["Content-Type"] = "application/json"
            return response

        if new_password := request.form.get("password"):
            has_changed = True
            user.set_password(new_password)
            flash("Password changed", "success")

        if new_email := request.form.get("email"):
            if new_email != user.email:
                has_changed = True
                update_email(user, new_email)
                flash("Email updated, please check your email to continue", "success")

        if not has_changed:
            flash("No changes made", "info")

        return redirect("/")

    return render_template("pages/settings.html.j2", page="account", email=user.email)
