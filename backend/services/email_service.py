"""Email Service for Booking Notifications"""

from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class EmailTemplate:
    subject: str
    body: str
    recipient: str
    sender: str = "noreply@seturmarinas.com"


class EmailService:
    """Email service for booking confirmations (POC - Mock mode)"""

    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.sent_emails = []

    def send_booking_confirmation(
        self,
        booking_data: Dict,
        customer_email: str,
        marina_name: str
    ) -> bool:
        subject = f"Setur Marina Rezervasyon Onayı - {booking_data['booking_id']}"

        body = f"""
╔═══════════════════════════════════════════════╗
║          SETUR MARINA                         ║
║      Rezervasyon Onay Belgesi                 ║
╚═══════════════════════════════════════════════╝

Sayın {booking_data['customer_name']},

{marina_name} rezervasyonunuz başarıyla oluşturulmuştur.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REZERVASYON DETAYLARI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Rezervasyon No:    {booking_data['booking_id']}
Tekne Adı:         {booking_data['boat_name']}
Tekne Boyu:        {booking_data['boat_length_meters']}m

Check-in:          {booking_data['check_in']}
Check-out:         {booking_data['check_out']}
Toplam Gece:       {booking_data['total_nights']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ÖDEME BİLGİLERİ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Toplam Tutar:      €{booking_data['total_price_eur']}

İyi seyirler dileriz!

Setur Marina Team
www.seturmarinas.com
"""

        return self._send_email(
            recipient=customer_email,
            subject=subject,
            body=body
        )

    def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        email = EmailTemplate(
            recipient=recipient,
            subject=subject,
            body=body
        )

        if self.mock_mode:
            print("\n" + "="*60)
            print("📧 EMAIL SENT (MOCK MODE)")
            print("="*60)
            print(f"To: {recipient}")
            print(f"Subject: {subject}")
            print("-"*60)
            print(body)
            print("="*60 + "\n")

            self.sent_emails.append({
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "sent_at": datetime.now().isoformat()
            })

            return True
        else:
            raise NotImplementedError("Production email service not configured")

    def get_sent_emails(self) -> list:
        return self.sent_emails


_email_service_instance: Optional[EmailService] = None


def get_email_service() -> EmailService:
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService(mock_mode=True)
    return _email_service_instance
