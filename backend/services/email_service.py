import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_notification_email(recipient_email, subject, message_body, meeting_link=None):
    """
    Dispatches notification email via SMTP.
    If SMTP credentials are not configured in .env, logs a clear notice and skips without error.
    """
    smtp_server = os.environ.get("SMTP_SERVER") or Config.SMTP_SERVER or "smtp.gmail.com"
    smtp_port = int(os.environ.get("SMTP_PORT") or Config.SMTP_PORT or 587)
    smtp_user = os.environ.get("SMTP_USERNAME") or Config.SMTP_USERNAME
    smtp_password = os.environ.get("SMTP_PASSWORD") or Config.SMTP_PASSWORD
    sender_email = os.environ.get("SMTP_SENDER_EMAIL") or Config.SMTP_SENDER_EMAIL or smtp_user

    if not smtp_user or not smtp_password or not recipient_email:
        print(f">> [SMTP] SMTP credentials not fully configured in .env. Skipping email dispatch to {recipient_email}.")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[Smart AI Assistant] {subject}"
        msg['From'] = sender_email
        msg['To'] = recipient_email

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #4f46e5; color: white; padding: 18px 24px;">
                <h2 style="margin: 0; font-size: 18px;">Smart AI Meeting Assistant</h2>
            </div>
            <div style="padding: 24px; color: #1e293b; line-height: 1.6;">
                <h3 style="margin-top: 0; color: #334155;">{subject}</h3>
                <p style="font-size: 15px;">{message_body}</p>
                {f'<div style="margin-top: 20px;"><a href="{meeting_link}" style="background-color: #4f46e5; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Open Application</a></div>' if meeting_link else ''}
            </div>
            <div style="background-color: #f8fafc; padding: 12px 24px; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
                This is an automated notification from your Smart AI Meeting Assistant system.
            </div>
        </div>
        """

        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        print(f">> [SMTP] Notification email successfully sent to: {recipient_email}")
        return True

    except Exception as e:
        print(f">> [SMTP Warning] Could not send email to {recipient_email}: {e}")
        return False
