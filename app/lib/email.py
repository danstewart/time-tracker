import sendgrid
from app.lib.logger import get_logger
from flask import current_app as app

logger = get_logger(__name__)


def send_email(to_email: str, subject: str, html: str):
    """
    Sends an email

    `to_email`: List of email receipients as a comma separated string
    `subject`: The mail subject line
    `html`: The HTML mail body
    """
    message = sendgrid.Mail(
        from_email="noreply@danstewart.xyz",
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
