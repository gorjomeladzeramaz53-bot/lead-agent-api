import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Service for sending personalized cold outreach emails using SMTP."""

    def __init__(self) -> None:
        # Fetch SMTP configuration safely from settings with fallbacks
        self.smtp_host = getattr(settings, "SMTP_HOST", "smtp.example.com")
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_username = getattr(settings, "SMTP_USERNAME", "")
        
        # Handle SecretStr for smtp_password if defined in settings
        raw_password = getattr(settings, "SMTP_PASSWORD", "")
        if hasattr(raw_password, "get_secret_value"):
            self.smtp_password = raw_password.get_secret_value()
        else:
            self.smtp_password = str(raw_password)

        self.sender_email = getattr(settings, "SENDER_EMAIL", self.smtp_username)

    async def send_outreach_email(self, recipient_email: str, company_name: str, summary: str | None) -> bool:
        """
        Sends a personalized cold outreach email to a successfully scraped lead.
        Returns True if successful, False otherwise.
        """
        if not recipient_email:
            logger.warning("No recipient email provided for outreach. Skipping email dispatch.")
            return False

        subject = f"Collaboration Opportunity with {company_name}"
        
        # Craft a personalized body snippet utilizing the AI-generated summary/notes
        context_snippet = f" We noticed that your company focuses on: {summary}" if summary else ""
        body = (
            f"Hello,\n\n"
            f"I hope this email finds you well.{context_snippet}\n\n"
            f"We help businesses scale their operations through cutting-edge AI solutions. "
            f"I would love to connect and discuss how we might add value to {company_name}.\n\n"
            f"Best regards,\n"
            f"The Lead Agent Team"
        )

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        logger.info(f"Attempting to send outreach email to {recipient_email} for company {company_name}...")

        try:
            # Using Python's built-in smtplib securely
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)

            logger.info(f"Successfully sent outreach email to {recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication failed. Check your username and password settings.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred while sending email to {recipient_email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending email to {recipient_email}: {str(e)}")
            return False