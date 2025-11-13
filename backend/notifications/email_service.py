"""
Email Notification Service
Sends compliance alerts, permit notifications, and violation warnings
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

# SMTP Configuration from environment
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "Ada Maritime AI <noreply@adamaritime.ai>")


class EmailService:
    """Email notification service for Ada Maritime AI"""

    def __init__(
        self,
        smtp_host: str = SMTP_HOST,
        smtp_port: int = SMTP_PORT,
        smtp_user: str = SMTP_USER,
        smtp_password: str = SMTP_PASSWORD,
        from_email: str = SMTP_FROM
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send email via SMTP

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body (optional)
            attachments: List of attachments [{filename, content, mimetype}]

        Returns:
            True if email sent successfully
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(to_emails)

            # Add plain text version
            if body_text:
                msg.attach(MIMEText(body_text, "plain"))

            # Add HTML version
            msg.attach(MIMEText(body_html, "html"))

            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEApplication(
                        attachment["content"],
                        Name=attachment["filename"]
                    )
                    part["Content-Disposition"] = f'attachment; filename="{attachment["filename"]}"'
                    msg.attach(part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_emails, msg.as_string())

            logger.info(f"Email sent to {to_emails}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    # === Compliance Notifications ===

    def send_violation_alert(
        self,
        to_emails: List[str],
        violation: Dict[str, Any],
        marina_name: str
    ) -> bool:
        """
        Send violation alert email

        Args:
            to_emails: Recipients
            violation: Violation details
            marina_name: Marina name

        Returns:
            True if sent successfully
        """
        severity_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "⚡",
            "low": "ℹ️"
        }

        emoji = severity_emoji.get(violation.get("severity", "medium"), "⚠️")

        subject = f"{emoji} Compliance Violation - Article {violation.get('article_number')}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #f44336; color: white; padding: 20px; border-radius: 5px;">
                <h2>{emoji} Compliance Violation Detected</h2>
            </div>

            <div style="padding: 20px;">
                <h3>Violation Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Marina:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{marina_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Article:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{violation.get('article_number')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Severity:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{violation.get('severity', 'N/A').upper()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Description:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{violation.get('description', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Detected:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{violation.get('detected_at', 'N/A')}</td>
                    </tr>
                </table>

                <div style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <strong>Required Actions:</strong>
                    <ul>
                        {"".join([f"<li>{action}</li>" for action in violation.get('required_actions', [])])}
                    </ul>
                </div>

                <p style="margin-top: 20px;">
                    <strong>Response Time Required:</strong> {violation.get('response_time_hours', 'N/A')} hours
                </p>

                <div style="margin-top: 30px; text-align: center;">
                    <a href="http://dashboard.adamaritime.ai/violations/{violation.get('violation_id')}"
                       style="background-color: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                        View Details & Resolve
                    </a>
                </div>
            </div>

            <div style="margin-top: 30px; padding: 20px; background-color: #f5f5f5; text-align: center; font-size: 12px; color: #666;">
                Ada Maritime AI - Compliance Management System<br>
                This is an automated notification. Please do not reply to this email.
            </div>
        </body>
        </html>
        """

        return self.send_email(to_emails, subject, html_body)

    def send_insurance_expiry_warning(
        self,
        to_emails: List[str],
        vessel_name: str,
        vessel_registration: str,
        expiry_date: str,
        days_until_expiry: int
    ) -> bool:
        """
        Send insurance expiry warning

        Args:
            to_emails: Vessel owner/manager emails
            vessel_name: Vessel name
            vessel_registration: Registration number
            expiry_date: Insurance expiry date
            days_until_expiry: Days until expiration

        Returns:
            True if sent successfully
        """
        subject = f"⚠️ Insurance Expiring Soon - {vessel_name}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #ff9800; color: white; padding: 20px; border-radius: 5px;">
                <h2>⚠️ Insurance Renewal Required</h2>
            </div>

            <div style="padding: 20px;">
                <p>Dear Vessel Owner,</p>

                <p>This is a reminder that the insurance policy for <strong>{vessel_name}</strong>
                is expiring in <strong>{days_until_expiry} days</strong>.</p>

                <h3>Vessel Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Vessel Name:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{vessel_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Registration:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{vessel_registration}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Expiry Date:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{expiry_date}</td>
                    </tr>
                </table>

                <div style="margin-top: 20px; padding: 15px; background-color: #ffebee; border-left: 4px solid #f44336;">
                    <strong>⚠️ Important Notice:</strong><br>
                    Per Article E.2.1 of the Marina Operation Regulations, vessels without valid insurance
                    are not permitted to remain in the marina. Please renew your insurance policy before
                    the expiry date to avoid service interruption.
                </div>

                <p style="margin-top: 20px;">
                    To update your insurance information, please contact the marina office or
                    upload your renewed policy through the marina portal.
                </p>

                <div style="margin-top: 30px; text-align: center;">
                    <a href="http://dashboard.adamaritime.ai/insurance/renew"
                       style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                        Upload Renewed Policy
                    </a>
                </div>
            </div>

            <div style="margin-top: 30px; padding: 20px; background-color: #f5f5f5; text-align: center; font-size: 12px; color: #666;">
                Ada Maritime AI - Compliance Management System
            </div>
        </body>
        </html>
        """

        return self.send_email(to_emails, subject, html_body)

    def send_permit_approved(
        self,
        to_emails: List[str],
        permit: Dict[str, Any],
        marina_name: str
    ) -> bool:
        """
        Send hot work permit approval notification

        Args:
            to_emails: Requester emails
            permit: Permit details
            marina_name: Marina name

        Returns:
            True if sent successfully
        """
        subject = f"✅ Hot Work Permit Approved - {permit.get('work_location')}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #4CAF50; color: white; padding: 20px; border-radius: 5px;">
                <h2>✅ Hot Work Permit Approved</h2>
            </div>

            <div style="padding: 20px;">
                <p>Your hot work permit request has been approved.</p>

                <h3>Permit Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Permit ID:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{permit.get('permit_id')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Location:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{permit.get('work_location')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Work Description:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{permit.get('work_description')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Scheduled Start:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{permit.get('scheduled_start')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Scheduled End:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{permit.get('scheduled_end')}</td>
                    </tr>
                </table>

                <div style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <strong>⚠️ Safety Requirements (Article E.5.5):</strong>
                    <ul>
                        <li>Fire watch must be present at all times</li>
                        <li>Fire extinguisher must be readily available</li>
                        <li>Area must be clear of flammable materials</li>
                        <li>Work must be completed by scheduled end time</li>
                        <li>Notify marina office when work begins and ends</li>
                    </ul>
                </div>

                {"<p style='margin-top: 15px; color: #d32f2f;'><strong>🔥 Fire Watch Required:</strong> A designated fire watch person must be present during all hot work activities.</p>" if permit.get('fire_watch_required') else ""}

                <div style="margin-top: 30px; text-align: center;">
                    <a href="http://dashboard.adamaritime.ai/permits/{permit.get('permit_id')}"
                       style="background-color: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                        View Permit Details
                    </a>
                </div>
            </div>

            <div style="margin-top: 30px; padding: 20px; background-color: #f5f5f5; text-align: center; font-size: 12px; color: #666;">
                Ada Maritime AI - Permit Management System
            </div>
        </body>
        </html>
        """

        return self.send_email(to_emails, subject, html_body)

    def send_daily_compliance_report(
        self,
        to_emails: List[str],
        marina_name: str,
        audit_summary: Dict[str, Any]
    ) -> bool:
        """
        Send daily compliance audit report

        Args:
            to_emails: Marina manager emails
            marina_name: Marina name
            audit_summary: Audit summary data

        Returns:
            True if sent successfully
        """
        subject = f"📊 Daily Compliance Report - {marina_name} - {datetime.now().strftime('%Y-%m-%d')}"

        summary = audit_summary.get("summary", {})
        violations_by_severity = summary.get("by_severity", {})

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #1976D2; color: white; padding: 20px; border-radius: 5px;">
                <h2>📊 Daily Compliance Report</h2>
                <p>{marina_name} - {datetime.now().strftime('%B %d, %Y')}</p>
            </div>

            <div style="padding: 20px;">
                <h3>Summary</h3>
                <div style="display: flex; justify-content: space-around; margin: 20px 0;">
                    <div style="text-align: center; padding: 15px; background-color: #f44336; color: white; border-radius: 5px; min-width: 100px;">
                        <div style="font-size: 32px; font-weight: bold;">{violations_by_severity.get('critical', 0)}</div>
                        <div>Critical</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background-color: #ff9800; color: white; border-radius: 5px; min-width: 100px;">
                        <div style="font-size: 32px; font-weight: bold;">{violations_by_severity.get('high', 0)}</div>
                        <div>High</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background-color: #ffc107; color: white; border-radius: 5px; min-width: 100px;">
                        <div style="font-size: 32px; font-weight: bold;">{violations_by_severity.get('medium', 0)}</div>
                        <div>Medium</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background-color: #2196F3; color: white; border-radius: 5px; min-width: 100px;">
                        <div style="font-size: 32px; font-weight: bold;">{violations_by_severity.get('low', 0)}</div>
                        <div>Low</div>
                    </div>
                </div>

                <h3>Statistics</h3>
                <ul>
                    <li>Total Active Violations: <strong>{summary.get('total_active_violations', 0)}</strong></li>
                    <li>Resolved Today: <strong>{summary.get('resolved_today', 0)}</strong></li>
                    <li>New Violations: <strong>{summary.get('new_violations', 0)}</strong></li>
                    <li>Active Hot Work Permits: <strong>{summary.get('active_permits', 0)}</strong></li>
                    <li>Insurance Expiring Soon: <strong>{summary.get('insurance_expiring_soon', 0)}</strong></li>
                </ul>

                <div style="margin-top: 30px; text-align: center;">
                    <a href="http://dashboard.adamaritime.ai/compliance/report"
                       style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                        View Full Report
                    </a>
                </div>
            </div>

            <div style="margin-top: 30px; padding: 20px; background-color: #f5f5f5; text-align: center; font-size: 12px; color: #666;">
                Ada Maritime AI - Automated Daily Report
            </div>
        </body>
        </html>
        """

        return self.send_email(to_emails, subject, html_body)


# Singleton instance
_email_service_instance = None


def get_email_service() -> EmailService:
    """Get email service singleton instance"""
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance
