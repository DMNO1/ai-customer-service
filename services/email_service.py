"""
Email Service for AI Customer Service System
Handles transactional emails using SMTP with async support
"""

import logging
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import jinja2

# Try to import aiosmtplib for async support
try:
    import aiosmtplib
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    logging.warning("aiosmtplib not installed, using synchronous SMTP only")


class EmailTemplate:
    """
    Email template helper using Jinja2
    """
    
    def __init__(self, template_dir: str = "./email_templates"):
        """
        Initialize template engine
        
        Args:
            template_dir: Directory containing HTML/Text templates
        """
        self.template_dir = template_dir
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def render(self, template_name: str, **context) -> str:
        """
        Render a template
        
        Args:
            template_name: Template file name (without extension)
            **context: Template variables
            
        Returns:
            Rendered HTML string
        """
        # Try with .html extension first, then .txt
        for ext in ['.html', '.txt']:
            try:
                template = self.env.get_template(f"{template_name}{ext}")
                return template.render(**context)
            except jinja2.TemplateNotFound:
                continue
        
        raise jinja2.TemplateNotFound(f"Template '{template_name}' not found")


class EmailService:
    """
    Email service for sending transactional emails
    """
    
    # Email templates registry (name -> subject template)
    TEMPLATE_REGISTRY = {
        "welcome": {
            "subject": "Welcome to AI Customer Service System, {{ name }}!",
            "template": "welcome_email"
        },
        "account_verification": {
            "subject": "Verify your email - AI Customer Service",
            "template": "verification_email"
        },
        "password_reset": {
            "subject": "Password Reset - AI Customer Service",
            "template": "password_reset"
        },
        "subscription_confirmation": {
            "subject": "Subscription Confirmed - {{ plan_name }}",
            "template": "subscription_confirmation"
        },
        "subscription_invoice": {
            "subject": "Invoice #{{ invoice_id }} - {{ amount }}",
            "template": "invoice"
        },
        "payment_receipt": {
            "subject": "Payment Receipt - {{ amount }}",
            "template": "payment_receipt"
        },
        "subscription_renewal_reminder": {
            "subject": "Your subscription renews in {{ days }} days",
            "template": "renewal_reminder"
        },
        "subscription_canceled": {
            "subject": "Subscription Canceled",
            "template": "subscription_canceled"
        }
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize email service
        
        Args:
            config: Configuration dictionary with SMTP settings
        """
        self.config = config or {}
        self.smtp_host = self.config.get("smtp_server") or os.getenv("SMTP_SERVER")
        self.smtp_port = int(self.config.get("smtp_port") or os.getenv("SMTP_PORT", 587))
        self.smtp_username = self.config.get("smtp_username") or os.getenv("SMTP_USERNAME")
        self.smtp_password = self.config.get("smtp_password") or os.getenv("SMTP_PASSWORD")
        self.smtp_use_tls = self.config.get("smtp_use_tls", True)
        self.default_from = self.config.get("default_from", "noreply@ai-customer-service.com")
        
        self.template_engine = None
        if os.path.exists(self.config.get("template_dir", "./email_templates")):
            self.template_engine = EmailTemplate(self.config.get("template_dir"))
        
        logging.info("EmailService initialized")
    
    def _get_connection(self) -> smtplib.SMTP:
        """
        Create SMTP connection
        
        Returns:
            Connected SMTP client
        """
        if not all([self.smtp_host, self.smtp_username, self.smtp_password]):
            raise ValueError("SMTP configuration incomplete")
        
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        if self.smtp_use_tls:
            server.starttls()
        server.login(self.smtp_username, self.smtp_password)
        return server
    
    async def _send_async(self, msg: MIMEMultipart) -> bool:
        """
        Send email asynchronously
        
        Args:
            msg: Prepared email message
            
        Returns:
            Success status
        """
        if not ASYNC_AVAILABLE:
            raise RuntimeError("aiosmtplib not installed, cannot send async emails")
        
        try:
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=self.smtp_use_tls,
                username=self.smtp_username,
                password=self.smtp_password
            )
            return True
        except Exception as e:
            logging.error(f"Async email send failed: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None,
                   from_email: Optional[str] = None, attachments: Optional[List[Dict]] = None) -> Dict:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML body content
            text_body: Plain text alternative (optional)
            from_email: Sender email (uses default if None)
            attachments: List of attachment dicts with 'filename', 'content', 'mime_type'
            
        Returns:
            Result dictionary with success status
        """
        from_email = from_email or self.default_from
        
        # Create message
        if text_body:
            msg = MIMEMultipart('alternative')
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(text_part)
            msg.attach(html_part)
        else:
            msg = MIMEMultipart()
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
        
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f"attachment; filename={attachment['filename']}"
                )
                msg.attach(part)
        
        # Send email
        try:
            server = self._get_connection()
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email sent to {to_email}: {subject}")
            return {"success": True, "to": to_email, "subject": subject}
            
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {e}")
            return {"success": False, "error": str(e), "to": to_email, "subject": subject}
    
    async def send_email_async(self, to_email: str, subject: str, html_body: str,
                             text_body: Optional[str] = None, from_email: Optional[str] = None) -> Dict:
        """
        Send an email asynchronously
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML body content
            text_body: Plain text alternative (optional)
            from_email: Sender email
            
        Returns:
            Result dictionary
        """
        if not ASYNC_AVAILABLE:
            return {"success": False, "error": "Async email not available (aiosmtplib missing)"}
        
        # Similar to send_email but uses async
        from_email = from_email or self.default_from
        
        msg = MIMEMultipart('alternative')
        if text_body:
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            msg.attach(text_part)
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        try:
            success = await self._send_async(msg)
            if success:
                logging.info(f"Async email sent to {to_email}: {subject}")
                return {"success": True, "to": to_email, "subject": subject}
            else:
                return {"success": False, "error": "Async send failed", "to": to_email}
        except Exception as e:
            logging.error(f"Async email send failed: {e}")
            return {"success": False, "error": str(e), "to": to_email}
    
    def send_template_email(self, to_email: str, template_name: str, context: Dict[str, Any],
                          from_email: Optional[str] = None) -> Dict:
        """
        Send an email using a template
        
        Args:
            to_email: Recipient email
            template_name: Name of the registered template
            context: Template context variables
            from_email: Sender email
            
        Returns:
            Result dictionary
        """
        if not self.template_engine:
            return {"success": False, "error": "Template engine not initialized"}
        
        if template_name not in self.TEMPLATE_REGISTRY:
            return {"success": False, "error": f"Unknown template: {template_name}"}
        
        template_info = self.TEMPLATE_REGISTRY[template_name]
        
        try:
            # Render HTML and text versions
            html_body = self.template_engine.render(template_info["template"], **context)
            # Generate plain text from HTML (simple fallback)
            text_body = jinja2.Markup(html_body).striptags()
            
            # Render subject
            subject_template = jinja2.Template(template_info["subject"])
            subject = subject_template.render(**context)
            
            return self.send_email(to_email, subject, html_body, text_body, from_email)
            
        except Exception as e:
            logging.error(f"Failed to render template {template_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def send_welcome_email(self, to_email: str, user_name: str, dashboard_url: str) -> Dict:
        """
        Send welcome email to new user
        
        Args:
            to_email: User email
            user_name: User's full name
            dashboard_url: URL to dashboard
            
        Returns:
            Result dictionary
        """
        context = {
            "name": user_name,
            "dashboard_url": dashboard_url,
            "current_year": datetime.now().year
        }
        return self.send_template_email(to_email, "welcome", context)
    
    def send_subscription_confirmation(self, to_email: str, user_name: str, plan_name: str,
                                     amount: float, start_date: datetime, end_date: datetime) -> Dict:
        """
        Send subscription confirmation
        
        Args:
            to_email: User email
            user_name: User's full name
            plan_name: Plan name
            amount: Subscription amount
            start_date: Subscription start date
            end_date: Subscription end date
            
        Returns:
            Result dictionary
        """
        context = {
            "name": user_name,
            "plan_name": plan_name,
            "amount": f"{amount:.2f}",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "current_year": datetime.now().year
        }
        return self.send_template_email(to_email, "subscription_confirmation", context)


def test_email_service():
    """
    Test the email service
    """
    print("Testing Email Service...")
    
    service = EmailService()
    
    print("SMTP Configuration:")
    print(f"  Host: {service.smtp_host or 'Not set'}")
    print(f"  Port: {service.smtp_port}")
    print(f"  Username: {service.smtp_username or 'Not set'}")
    print(f"  Templates: {'Enabled' if service.template_engine else 'Disabled'}")
    
    print("EmailService initialized")
    

if __name__ == "__main__":
    test_email_service()