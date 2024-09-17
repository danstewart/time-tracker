from flask import Blueprint

from app.lib.logger import get_logger

v = Blueprint("callback", __name__)
logger = get_logger(__name__)


@v.route("/callback/slack", methods=["GET"])
def slack_oauth_callback():
    import requests
    from flask import current_app as app
    from flask import flash, redirect, request

    from app import db
    from app.controllers import settings
    from app.controllers.user.util import get_user
    from app.models import UserToSlackToken

    current_user = get_user()
    if not current_user:
        flash("You need to be logged in to connect your slack account", "danger")
        return redirect("/login")

    code = request.args.get("code")

    resp = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": app.config["SLACK_CLIENT_ID"],
            "client_secret": app.config["SLACK_CLIENT_SECRET"],
            "code": code,
            "redirect_uri": f"{app.config['HOST']}/callback/slack",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    parsed = resp.json()

    if parsed.get("ok") != True:
        import rollbar

        rollbar.report_message(f"Slack OAuth callback failed: {parsed}", level="error")
        flash("Something went wrong, please try again.", "danger")
        return redirect("/settings/slack")

    access_token = parsed["authed_user"]["access_token"]
    db.session.add(UserToSlackToken(user_id=current_user.id, slack_token=access_token))
    settings.update(auto_update_slack_status=True)
    db.session.commit()

    flash("Your slack account has been connected", "success")
    return redirect("/settings/slack")
