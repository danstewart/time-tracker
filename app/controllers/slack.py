import requests

from app.controllers import settings
from app.controllers.user.util import get_user


def update_status(on_break: bool):
    user = get_user()
    _settings = settings.fetch()
    if not _settings.auto_update_slack_status:
        return

    message, emoji = ("Away", ":running:")
    if not on_break:
        message, emoji = ("", "")

    requests.post(
        "https://slack.com/api/users.profile.set",
        headers={
            "Content-Type": "application/json",
            # TODO: Handle multiple tokens
            "Authorization": "Bearer " + user.slack_tokens[0].slack_token,
        },
        json={
            "profile": {
                "status_text": message,
                "status_emoji": emoji,
                "status_expiration": 0,
            },
        },
    )
