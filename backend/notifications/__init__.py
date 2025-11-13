"""
Notifications Module
Email and push notification services for Ada Maritime AI
"""

from .email_service import EmailService, get_email_service

__all__ = ["EmailService", "get_email_service"]
