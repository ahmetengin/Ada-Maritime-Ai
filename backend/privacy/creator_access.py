"""
Creator Access Management
Special access layer for system creators/developers

IMPORTANT: Creator has full access for development and debugging,
but with complete transparency and captain notification.

Principle: "Creator can access everything, but captain knows everything"
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import time
import hashlib
import secrets


class AccessReason(Enum):
    """Reasons for creator access"""
    DEVELOPMENT = "development"
    DEBUGGING = "debugging"
    MAINTENANCE = "maintenance"
    SECURITY_AUDIT = "security_audit"
    BUG_FIX = "bug_fix"
    FEATURE_DEVELOPMENT = "feature_development"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    EMERGENCY_SUPPORT = "emergency_support"


class AccessLevel(Enum):
    """Access levels in the system"""
    CREATOR = "creator"  # Full system access
    CAPTAIN = "captain"  # Data ownership & operational control
    CREW = "crew"  # Limited operational access
    EXTERNAL = "external"  # No access by default


@dataclass
class CreatorAccessToken:
    """
    Time-limited access token for creator
    """
    token_id: str
    creator_id: str
    reason: AccessReason
    justification: str
    issued_at: float
    expires_at: float
    scope: List[str]
    captain_notified: bool = False
    captain_approved: bool = False  # For sensitive operations

    def __post_init__(self):
        if not self.token_id:
            self.token_id = self._generate_token()

    def _generate_token(self) -> str:
        """Generate secure access token"""
        return secrets.token_hex(32)

    def is_valid(self) -> bool:
        """Check if token is still valid"""
        return time.time() < self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            'token_id': self.token_id,
            'creator_id': self.creator_id,
            'reason': self.reason.value,
            'justification': self.justification,
            'issued_at': self.issued_at,
            'expires_at': self.expires_at,
            'scope': self.scope,
            'captain_notified': self.captain_notified,
            'captain_approved': self.captain_approved,
        }


class CreatorAccessManager:
    """
    Manages creator/developer access with transparency

    Principles:
    1. Creator CAN access everything (for development)
    2. ALL creator access is logged
    3. Captain is ALWAYS notified
    4. Captain CAN see all creator actions
    5. Captain CAN revoke creator access
    6. Sensitive operations require captain approval
    """

    def __init__(self, captain_id: str):
        """
        Initialize creator access manager

        Args:
            captain_id: The captain who owns the data
        """
        self.captain_id = captain_id
        self.active_tokens: Dict[str, CreatorAccessToken] = {}
        self.access_log: List[Dict[str, Any]] = []
        self.creator_access_enabled = True  # Captain can disable
        self.require_approval_for_sensitive = True

    def request_creator_access(
        self,
        creator_id: str,
        reason: AccessReason,
        justification: str,
        duration_hours: int = 24,
        scope: Optional[List[str]] = None,
        sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        Request creator access

        Args:
            creator_id: Creator's identifier
            reason: Reason for access
            justification: Detailed explanation
            duration_hours: How long access is needed
            scope: What will be accessed
            sensitive: Whether this is sensitive operation

        Returns:
            Access token or approval required
        """

        # Check if creator access is enabled
        if not self.creator_access_enabled:
            return {
                'success': False,
                'reason': 'Creator access has been disabled by captain'
            }

        # Create access token
        token = CreatorAccessToken(
            token_id="",
            creator_id=creator_id,
            reason=reason,
            justification=justification,
            issued_at=time.time(),
            expires_at=time.time() + (duration_hours * 3600),
            scope=scope or ['full_system'],
            captain_notified=False,
            captain_approved=False
        )

        # For sensitive operations, require captain approval
        if sensitive and self.require_approval_for_sensitive:
            return {
                'success': False,
                'requires_approval': True,
                'token': token.to_dict(),
                'captain_notification': self._create_captain_notification(token)
            }

        # Grant access
        self.active_tokens[token.token_id] = token

        # Notify captain
        self._notify_captain(token)
        token.captain_notified = True

        # Log access grant
        self._log_creator_action(
            creator_id=creator_id,
            action='access_granted',
            reason=reason.value,
            token_id=token.token_id
        )

        return {
            'success': True,
            'token': token.to_dict(),
            'message': 'Creator access granted. Captain notified.',
            'warning': '⚠️  All actions will be logged and visible to captain'
        }

    def validate_creator_access(
        self,
        token_id: str,
        action: str
    ) -> Dict[str, bool]:
        """
        Validate creator access for an action

        Args:
            token_id: Access token
            action: What action creator wants to perform

        Returns:
            Validation result
        """

        if token_id not in self.active_tokens:
            return {
                'valid': False,
                'reason': 'Invalid or expired token'
            }

        token = self.active_tokens[token_id]

        if not token.is_valid():
            return {
                'valid': False,
                'reason': 'Token expired'
            }

        # Log the action
        self._log_creator_action(
            creator_id=token.creator_id,
            action=action,
            reason=token.reason.value,
            token_id=token_id
        )

        return {
            'valid': True,
            'creator_id': token.creator_id,
            'reason': token.reason.value
        }

    def creator_access_data(
        self,
        token_id: str,
        data_type: str,
        data: Any,
        action: str
    ) -> Dict[str, Any]:
        """
        Creator accesses data (with full transparency)

        Args:
            token_id: Access token
            data_type: Type of data accessed
            data: The data accessed
            action: What was done

        Returns:
            Access result
        """

        # Validate token
        validation = self.validate_creator_access(token_id, action)
        if not validation['valid']:
            return {
                'success': False,
                'reason': validation['reason']
            }

        # Allow access (creator has full access)
        # BUT: Log everything
        self._log_creator_action(
            creator_id=validation['creator_id'],
            action=f'data_access:{action}',
            reason=validation['reason'],
            token_id=token_id,
            details={
                'data_type': data_type,
                'data_hash': hashlib.sha256(str(data).encode()).hexdigest()[:16],
                'timestamp': time.time()
            }
        )

        # Notify captain of data access
        self._notify_captain_data_access(
            creator_id=validation['creator_id'],
            data_type=data_type,
            action=action
        )

        return {
            'success': True,
            'data': data,
            'logged': True,
            'captain_notified': True
        }

    def captain_approve_creator_access(
        self,
        token_id: str,
        approved: bool,
        captain_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Captain approves or denies creator access

        Voice: "Ada, creator access'i onayla/reddet"
        """

        if token_id not in self.active_tokens:
            return {
                'success': False,
                'reason': 'Token not found'
            }

        token = self.active_tokens[token_id]
        token.captain_approved = approved

        if approved:
            # Log approval
            self._log_creator_action(
                creator_id=token.creator_id,
                action='captain_approved',
                reason=token.reason.value,
                token_id=token_id,
                details={'captain_note': captain_note}
            )

            return {
                'success': True,
                'message': 'Creator access approved',
                'token': token.to_dict()
            }
        else:
            # Revoke access
            del self.active_tokens[token_id]

            self._log_creator_action(
                creator_id=token.creator_id,
                action='captain_denied',
                reason=token.reason.value,
                token_id=token_id,
                details={'captain_note': captain_note}
            )

            return {
                'success': True,
                'message': 'Creator access denied and revoked',
                'token_id': token_id
            }

    def captain_revoke_creator_access(
        self,
        token_id: Optional[str] = None,
        creator_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Captain revokes creator access

        Voice: "Ada, creator access'i iptal et"
        """

        if token_id:
            # Revoke specific token
            if token_id in self.active_tokens:
                token = self.active_tokens[token_id]
                del self.active_tokens[token_id]

                self._log_creator_action(
                    creator_id=token.creator_id,
                    action='captain_revoked',
                    reason='captain_decision',
                    token_id=token_id
                )

                return {
                    'success': True,
                    'message': f'Creator access token {token_id} revoked'
                }
            else:
                return {
                    'success': False,
                    'reason': 'Token not found'
                }

        elif creator_id:
            # Revoke all tokens for creator
            revoked = []
            for tid, token in list(self.active_tokens.items()):
                if token.creator_id == creator_id:
                    del self.active_tokens[tid]
                    revoked.append(tid)

            return {
                'success': True,
                'message': f'Revoked {len(revoked)} tokens for creator {creator_id}',
                'revoked_tokens': revoked
            }

        else:
            # Revoke ALL creator access
            count = len(self.active_tokens)
            self.active_tokens.clear()

            return {
                'success': True,
                'message': f'Revoked all creator access ({count} tokens)',
                'count': count
            }

    def captain_disable_creator_access(self) -> Dict[str, Any]:
        """
        Captain completely disables creator access

        Voice: "Ada, creator access'i tamamen kapat"
        """

        self.creator_access_enabled = False

        # Revoke all active tokens
        count = len(self.active_tokens)
        self.active_tokens.clear()

        return {
            'success': True,
            'message': 'Creator access completely disabled',
            'revoked_tokens': count,
            'warning': '⚠️  System updates and debugging will be limited'
        }

    def captain_enable_creator_access(self) -> Dict[str, Any]:
        """
        Captain re-enables creator access

        Voice: "Ada, creator access'i aktif et"
        """

        self.creator_access_enabled = True

        return {
            'success': True,
            'message': 'Creator access enabled'
        }

    def get_creator_access_log(
        self,
        creator_id: Optional[str] = None,
        hours: int = 168
    ) -> List[Dict[str, Any]]:
        """
        Get log of all creator actions

        Voice: "Ada, creator ne yaptı?"
        """

        cutoff = time.time() - (hours * 3600)

        log = [
            entry for entry in self.access_log
            if entry['timestamp'] >= cutoff
        ]

        if creator_id:
            log = [e for e in log if e.get('creator_id') == creator_id]

        return log

    def get_active_creator_access(self) -> List[Dict[str, Any]]:
        """
        Get all active creator access tokens

        Voice: "Ada, aktif creator access'leri göster"
        """

        return [token.to_dict() for token in self.active_tokens.values()]

    def _log_creator_action(
        self,
        creator_id: str,
        action: str,
        reason: str,
        token_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log creator action"""

        entry = {
            'timestamp': time.time(),
            'creator_id': creator_id,
            'action': action,
            'reason': reason,
            'token_id': token_id,
            'details': details or {}
        }

        self.access_log.append(entry)

    def _notify_captain(self, token: CreatorAccessToken):
        """
        Notify captain of creator access request
        """

        # In real implementation, would send notification
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║  CAPTAIN NOTIFICATION: Creator Access Request            ║
╟───────────────────────────────────────────────────────────╢
║  Creator: {token.creator_id}
║  Reason: {token.reason.value}
║  Justification: {token.justification}
║  Duration: {(token.expires_at - token.issued_at) / 3600:.1f} hours
║  Scope: {', '.join(token.scope)}
║
║  ⚠️  Creator will have access to system for debugging.
║  ⚠️  All actions will be logged and visible to you.
║
║  Voice: "Ada, creator access log'u göster"
╚═══════════════════════════════════════════════════════════╝
        """)

    def _notify_captain_data_access(
        self,
        creator_id: str,
        data_type: str,
        action: str
    ):
        """Notify captain of data access by creator"""

        # In real implementation, would send notification
        pass

    def _create_captain_notification(
        self,
        token: CreatorAccessToken
    ) -> str:
        """Create notification text for captain"""

        return f"""
Creator Access Request
━━━━━━━━━━━━━━━━━━━━━━
Creator: {token.creator_id}
Reason: {token.reason.value}
Justification: {token.justification}

This is a SENSITIVE operation requiring your approval.

Voice Commands:
- "Ada, creator access'i onayla"
- "Ada, creator access'i reddet"
"""


# Voice commands for captain
CREATOR_ACCESS_VOICE_COMMANDS = {
    'tr': {
        'show_log': [
            "creator ne yaptı",
            "creator access log'u göster",
            "creator erişim geçmişi"
        ],
        'show_active': [
            "aktif creator access'leri göster",
            "creator access durumu"
        ],
        'approve': [
            "creator access'i onayla",
            "creator erişimini onayla"
        ],
        'deny': [
            "creator access'i reddet",
            "creator erişimini reddet"
        ],
        'revoke': [
            "creator access'i iptal et",
            "creator erişimini kaldır"
        ],
        'disable': [
            "creator access'i tamamen kapat",
            "creator erişimini devre dışı bırak"
        ],
        'enable': [
            "creator access'i aktif et",
            "creator erişimini aç"
        ]
    },
    'en': {
        'show_log': [
            "what did creator do",
            "show creator access log",
            "creator access history"
        ],
        'show_active': [
            "show active creator access",
            "creator access status"
        ],
        'approve': [
            "approve creator access",
            "allow creator access"
        ],
        'deny': [
            "deny creator access",
            "reject creator access"
        ],
        'revoke': [
            "revoke creator access",
            "remove creator access"
        ],
        'disable': [
            "completely disable creator access",
            "turn off creator access"
        ],
        'enable': [
            "enable creator access",
            "turn on creator access"
        ]
    }
}
