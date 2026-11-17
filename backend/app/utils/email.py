"""
Email utility — works with Mailpit (SMTP) locally and Resend in production.
Email failures are logged but do NOT raise exceptions that would affect the caller.
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> bool:
    try:
        if settings.EMAIL_PROVIDER == "resend":
            return await _send_via_resend(to_email, subject, html_body, text_body)
        else:
            return await _send_via_smtp(to_email, subject, html_body, text_body)
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        return False


async def _send_via_smtp(to_email, subject, html_body, text_body=None):
    import aiosmtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email
    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USERNAME or None,
        password=settings.SMTP_PASSWORD or None,
        start_tls=False,
    )
    return True


async def _send_via_resend(to_email, subject, html_body, text_body=None):
    import resend
    resend.api_key = settings.RESEND_API_KEY
    params = {
        "from": f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html_body,
    }
    if text_body:
        params["text"] = text_body
    resend.Emails.send(params)
    return True


async def send_enquiry_notification(enquiry_data: dict) -> bool:
    subject = f"[Portfolio] New Enquiry: {enquiry_data.get('subject', '')}"
    name = enquiry_data.get("name", "")
    email = enquiry_data.get("email", "")
    enquiry_type = enquiry_data.get("enquiry_type", "general")
    message_preview = enquiry_data.get("message", "")[:300]
    admin_url = f"{settings.ADMIN_FRONTEND_URL}/admin/enquiries"

    html_body = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#111014;color:#F5F0FA;padding:32px">
<div style="max-width:600px;margin:0 auto;background:#19161F;border-radius:12px;border:1px solid #35303D">
<div style="background:#B794F6;padding:24px 32px"><h1 style="margin:0;color:#111014;font-size:20px">New Portfolio Enquiry</h1></div>
<div style="padding:32px">
<p><strong>From:</strong> {name} &lt;{email}&gt;</p>
<p><strong>Type:</strong> {enquiry_type.replace("_"," ").title()}</p>
<p><strong>Subject:</strong> {enquiry_data.get("subject","")}</p>
<div style="background:#201C27;padding:16px;border-radius:8px;border-left:3px solid #B794F6;margin-top:16px">
<p style="margin:0;color:#A9A1B1;font-size:13px">Message Preview</p>
<p style="margin:8px 0 0">{message_preview}</p></div>
<div style="margin-top:24px;text-align:center">
<a href="{admin_url}" style="background:#B794F6;color:#111014;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">View in Dashboard →</a>
</div></div></div></body></html>"""

    return await send_email(settings.NOTIFICATION_EMAIL, subject, html_body)


async def send_enquiry_acknowledgement(enquiry_data: dict) -> bool:
    name = enquiry_data.get("name", "there")
    email = enquiry_data.get("email", "")
    subject = "Thanks for reaching out!"

    html_body = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#111014;color:#F5F0FA;padding:32px">
<div style="max-width:600px;margin:0 auto;background:#19161F;border-radius:12px;border:1px solid #35303D">
<div style="background:#B794F6;padding:24px 32px"><h1 style="margin:0;color:#111014;font-size:20px">Message Received!</h1></div>
<div style="padding:32px">
<p>Hi {name},</p>
<p style="color:#A9A1B1">Thanks for reaching out! I've received your message and will get back to you as soon as possible — usually within 1–2 business days.</p>
<p style="color:#A9A1B1">In the meantime, feel free to explore my projects or connect with me on GitHub or LinkedIn.</p>
<p>Best,<br><strong>The Portfolio Owner</strong></p>
</div></div></body></html>"""

    return await send_email(email, subject, html_body)
