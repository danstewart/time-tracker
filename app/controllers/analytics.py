from os import getenv

from flask import current_app as app
from posthog import Posthog

posthog = Posthog(project_api_key=app.config["POSTHOG_KEY"], host="https://eu.i.posthog.com")

if getenv("TEST_MODE") == "yes":
    posthog.disabled = True
