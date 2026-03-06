import random
import string
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from utils.redis_client import delete_otp
import aiosmtplib
from core.config import settings
from jinja2 import Environment, FileSystemLoader
from utils.exception import EmailSendException

TEMPLATE_DIR = Path(__file__).resolve().parent / "email_templates"
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))

async def send_email(to_email: str, subject: str, otp: str, rollback_on_fail: bool):
    """
    Send an OTP email to the specified recipient.

    This function internally generates both the plain text and HTML versions
    of the OTP email using Jinja2 templates. The email is sent asynchronously
    via the SMTP server configured in `settings`.

    Args:
        to_email (str): Recipient email address.
        subject (str): Subject line for the email.
        otp (str): One-time password to include in the email.
        rollback_on_fail (bool): Whether to delete OTP on send failure.

    Raises:
        EmailSendException: If sending the email fails for any reason.
    """

    expiry_minutes = settings.OTP_EXPIRY // 60
    year = datetime.now().year

    # Render plain text
    plain_template = env.get_template("otp_email.txt")
    plain_text = plain_template.render(otp=otp, expiry_minutes=expiry_minutes)

    # Render HTML
    html_template = env.get_template("otp_email.html")
    html_body = html_template.render(otp=otp, expiry_minutes=expiry_minutes, year=year)

    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject

    # Attach plain text (fallback)
    message.set_content(plain_text)

    # Attach HTML (for modern clients)
    message.add_alternative(html_body, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASS,
            start_tls=True,
        )
    except Exception as e:
        # Rollback OTP if sending fails
        if rollback_on_fail:
            try:
                await delete_otp(to_email)
            except Exception as del_err:
                print(f"Failed to delete OTP after email failure: {del_err}")
        # Raise custom exception for monitoring/logging
        raise EmailSendException(email=to_email, message=str(e))
