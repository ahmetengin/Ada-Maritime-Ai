"""
Captain Consent Management System
Handles explicit approval requests for data sharing
"""

import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json


class ConsentMethod(Enum):
    """Method used to obtain consent"""
    VOICE = "voice"
    MANUAL = "manual"
    STANDING = "standing"  # Pre-approved standing permission


class ConsentStatus(Enum):
    """Status of consent request"""
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class ConsentRequest:
    """
    Request for captain consent to share data
    """
    destination: str  # Where data will be sent
    data_type: str  # Type of data to share
    data_size: int  # Size in bytes
    purpose: str  # Why data is needed
    timestamp: float = field(default_factory=time.time)
    request_id: str = field(default="")

    def __post_init__(self):
        if not self.request_id:
            # Generate unique request ID
            self.request_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique request ID"""
        data = f"{self.destination}:{self.data_type}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_voice_prompt(self, language: str = "tr") -> str:
        """Generate voice prompt for captain"""
        if language == "tr":
            return (
                f"Kaptan, {self.destination} için "
                f"{self.data_type} verisi paylaşılsın mı? "
                f"Amaç: {self.purpose}. "
                f"Cevap: 'Evet paylaş' veya 'Hayır'"
            )
        else:
            return (
                f"Captain, share {self.data_type} data "
                f"with {self.destination}? "
                f"Purpose: {self.purpose}. "
                f"Answer: 'Yes, share' or 'No'"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'request_id': self.request_id,
            'destination': self.destination,
            'data_type': self.data_type,
            'data_size': self.data_size,
            'purpose': self.purpose,
            'timestamp': self.timestamp,
        }


@dataclass
class ConsentResponse:
    """
    Captain's response to consent request
    """
    request_id: str
    granted: bool
    captain_id: str
    method: ConsentMethod
    confirmation_text: str = ""
    scope: Optional[Dict[str, Any]] = None  # What exactly was approved
    timestamp: float = field(default_factory=time.time)
    expiry: Optional[float] = None  # When consent expires (for standing permissions)
    conditions: List[str] = field(default_factory=list)  # Any conditions on consent

    def is_valid(self) -> bool:
        """Check if consent is still valid"""
        if not self.granted:
            return False
        if self.expiry and time.time() > self.expiry:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'request_id': self.request_id,
            'granted': self.granted,
            'captain_id': self.captain_id,
            'method': self.method.value,
            'confirmation_text': self.confirmation_text,
            'scope': self.scope,
            'timestamp': self.timestamp,
            'expiry': self.expiry,
            'conditions': self.conditions,
        }


class ConsentManager:
    """
    Manages captain consent for data sharing
    Implements explicit approval workflow
    """

    def __init__(self):
        self.pending_requests: Dict[str, ConsentRequest] = {}
        self.consent_history: List[ConsentResponse] = []
        self.standing_permissions: Dict[str, ConsentResponse] = {}

    async def request_captain_permission(
        self,
        destination: str,
        data_type: str,
        data_size: int,
        purpose: str
    ) -> ConsentRequest:
        """
        Create consent request for captain approval
        """
        request = ConsentRequest(
            destination=destination,
            data_type=data_type,
            data_size=data_size,
            purpose=purpose
        )

        # Store pending request
        self.pending_requests[request.request_id] = request

        return request

    async def voice_prompt(self, request: ConsentRequest, language: str = "tr") -> str:
        """
        Generate voice prompt for captain approval
        """
        return request.to_voice_prompt(language)

    async def process_captain_response(
        self,
        request_id: str,
        granted: bool,
        captain_id: str,
        method: ConsentMethod,
        confirmation_text: str = "",
        scope: Optional[Dict[str, Any]] = None,
        standing: bool = False,
        expiry_hours: Optional[int] = None
    ) -> ConsentResponse:
        """
        Process captain's consent response
        """
        if request_id not in self.pending_requests:
            raise ValueError(f"Invalid request ID: {request_id}")

        request = self.pending_requests[request_id]

        # Calculate expiry for standing permissions
        expiry = None
        if standing and expiry_hours:
            expiry = time.time() + (expiry_hours * 3600)

        response = ConsentResponse(
            request_id=request_id,
            granted=granted,
            captain_id=captain_id,
            method=method,
            confirmation_text=confirmation_text,
            scope=scope,
            expiry=expiry
        )

        # Store in history
        self.consent_history.append(response)

        # If standing permission, store it
        if standing and granted:
            key = f"{request.destination}:{request.data_type}"
            self.standing_permissions[key] = response

        # Remove from pending
        del self.pending_requests[request_id]

        return response

    def check_standing_permission(
        self,
        destination: str,
        data_type: str
    ) -> Optional[ConsentResponse]:
        """
        Check if there's a valid standing permission
        """
        key = f"{destination}:{data_type}"
        consent = self.standing_permissions.get(key)

        if consent and consent.is_valid():
            return consent

        # Remove expired permission
        if consent:
            del self.standing_permissions[key]

        return None

    def revoke_standing_permission(
        self,
        destination: str,
        data_type: str
    ) -> bool:
        """
        Revoke a standing permission
        """
        key = f"{destination}:{data_type}"
        if key in self.standing_permissions:
            del self.standing_permissions[key]
            return True
        return False

    def get_consent_history(
        self,
        captain_id: Optional[str] = None,
        destination: Optional[str] = None,
        hours: int = 168  # Default: last 7 days
    ) -> List[ConsentResponse]:
        """
        Get consent history with optional filters
        """
        cutoff_time = time.time() - (hours * 3600)
        history = [
            consent for consent in self.consent_history
            if consent.timestamp >= cutoff_time
        ]

        if captain_id:
            history = [c for c in history if c.captain_id == captain_id]

        if destination:
            history = [
                c for c in history
                if destination in self.pending_requests.get(c.request_id, ConsentRequest(
                    destination="", data_type="", data_size=0, purpose=""
                )).destination
            ]

        return history

    def get_standing_permissions(self) -> List[Dict[str, Any]]:
        """
        Get all active standing permissions
        """
        return [
            {
                'destination': key.split(':')[0],
                'data_type': key.split(':')[1],
                'granted_at': consent.timestamp,
                'expires_at': consent.expiry,
                'conditions': consent.conditions,
            }
            for key, consent in self.standing_permissions.items()
            if consent.is_valid()
        ]

    def clear_expired_permissions(self) -> int:
        """
        Clear expired standing permissions
        Returns number of permissions cleared
        """
        expired = [
            key for key, consent in self.standing_permissions.items()
            if not consent.is_valid()
        ]

        for key in expired:
            del self.standing_permissions[key]

        return len(expired)

    def export_consent_log(self) -> List[Dict[str, Any]]:
        """
        Export complete consent log for captain review
        """
        return [consent.to_dict() for consent in self.consent_history]

    async def request_with_auto_check(
        self,
        destination: str,
        data_type: str,
        data_size: int,
        purpose: str
    ) -> Optional[ConsentResponse]:
        """
        Request permission, but first check for standing permission
        Returns existing consent if available, None if new request needed
        """
        # Check standing permission first
        standing = self.check_standing_permission(destination, data_type)
        if standing:
            return standing

        # Need new request
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Export consent manager state"""
        return {
            'pending_requests': {
                k: v.to_dict() for k, v in self.pending_requests.items()
            },
            'consent_history': [c.to_dict() for c in self.consent_history],
            'standing_permissions': {
                k: v.to_dict() for k, v in self.standing_permissions.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsentManager':
        """Import consent manager state"""
        manager = cls()
        # Implementation for loading state would go here
        return manager
