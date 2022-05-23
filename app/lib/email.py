import sendgrid
from flask import current_app as app

from app.lib.logger import get_logger

logger = get_logger(__name__)


def send_email(to_email: str, subject: str, html: str):
    """
    Sends an email

    `to_email`: List of email receipients as a comma separated string
    `subject`: The mail subject line
    `html`: The HTML mail body
    """
    message = sendgrid.Mail(
        from_email=app.config["FROM_EMAIL"],
        to_emails=to_email,
        subject=subject,
        html_content=html,
    )

    try:
        sg = sendgrid.SendGridAPIClient(api_key=app.config["SENDGRID_API_KEY"])
        response = sg.send(message)
        return response
    except sendgrid.SendGridException as e:
        logger.exception(e)
