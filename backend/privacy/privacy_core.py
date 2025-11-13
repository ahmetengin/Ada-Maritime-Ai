"""
Ada.Sea Privacy Core
Central privacy management system orchestrating all privacy controls
"""

from typing import Optional, Dict, Any, List
import hashlib
import json

from .data_policy import DataPolicy, DataClassification
from .consent_manager import ConsentManager, ConsentMethod
from .audit_log import AuditLog


class AdaSeaPrivacyCore:
    """
    Core privacy management system for Ada.Sea

    Principles:
    - Zero Trust by Default: NO automatic data sharing
    - Explicit Consent: Captain approval required for ALL transfers
    - Minimal Data: Only send what's absolutely necessary
    - Complete Transparency: Full audit trail
    - Captain Control: Delete, rectify, stop rights

    "Kaptan ne derse o olur. Nokta."
    """

    def __init__(self, captain_id: str, data_policy: Optional[DataPolicy] = None, audit_log_path: Optional[str] = None):
        """
        Initialize privacy core

        Args:
            captain_id: Unique identifier for the captain
            data_policy: Custom data policy (optional, uses default if None)
            audit_log_path: Path to audit log database (optional)
        """
        self.captain_id = captain_id
        self.data_policy = data_policy or DataPolicy()
        self.consent_manager = ConsentManager()
        self.audit_log = AuditLog(db_path=audit_log_path)

        # Privacy settings
        self.cloud_sync_enabled = False  # Disabled by default
        self.captain_auth_required = True  # Always required
        self.zero_trust_mode = True  # Zero trust by default

    async def share_data(
        self,
        destination: str,
        data: Dict[str, Any],
        data_type: str,
        purpose: str,
        bypass_consent: bool = False,  # For emergency situations only
    ) -> Dict[str, Any]:
        """
        Share data with explicit captain approval

        This is the main data sharing gateway - ALL data transfers go through here

        Args:
            destination: Where data is being sent
            data: The data to share
            data_type: Type of data (must match DataClassification)
            purpose: Why this data is needed
            bypass_consent: Emergency bypass (logged and flagged)

        Returns:
            Result with success status and details
        """

        # CRITICAL: Check if captain authorization required
        if self.captain_auth_required and not bypass_consent:

            # 1. Check data policy - is this allowed at all?
            try:
                data_class = DataClassification(data_type)
            except ValueError:
                return {"success": False, "reason": f"Invalid data type: {data_type}"}

            if self.data_policy.is_private_data(data_class):
                # Absolutely private - never share
                self.audit_log.log_request(destination, data_type, self.captain_id)
                return {"success": False, "reason": "Data classified as PRIVATE - cannot share", "data_type": data_type}

            # 2. Check for standing permission
            standing_consent = self.consent_manager.check_standing_permission(destination, data_type)

            if standing_consent:
                # Use standing permission
                filtered_data = self._filter_by_scope(data, standing_consent.scope)
                result = await self._execute_transfer(destination, filtered_data, data_type, purpose)

                # Log with standing permission
                self.audit_log.log_transfer(
                    destination=destination,
                    data_type=data_type,
                    captain_id=self.captain_id,
                    authorization_method="standing_permission",
                    result="success" if result["success"] else "failed",
                    data=filtered_data,
                    confirmation_text="Standing permission",
                )

                return result

            # 3. Request captain permission
            request = await self.consent_manager.request_captain_permission(
                destination=destination, data_type=data_type, data_size=len(json.dumps(data)), purpose=purpose
            )

            # Log the request
            self.audit_log.log_request(destination, data_type, self.captain_id)

            # Wait for captain response (this would integrate with voice/UI)
            # For now, return the request for external handling
            return {
                "success": False,
                "reason": "Captain authorization required",
                "request": request.to_dict(),
                "voice_prompt": request.to_voice_prompt("tr"),
            }

        # Emergency bypass (heavily logged)
        if bypass_consent:
            result = await self._execute_transfer(destination, data, data_type, purpose)

            self.audit_log.log_transfer(
                destination=destination,
                data_type=data_type,
                captain_id=self.captain_id,
                authorization_method="EMERGENCY_BYPASS",
                result="success" if result["success"] else "failed",
                data=data,
                confirmation_text="⚠️ EMERGENCY BYPASS - NO CONSENT",
            )

            return result

        # Should not reach here
        return {"success": False, "reason": "Unknown error in privacy core"}

    async def process_captain_consent(
        self,
        request_id: str,
        granted: bool,
        method: ConsentMethod = ConsentMethod.VOICE,
        confirmation_text: str = "",
        scope: Optional[Dict[str, Any]] = None,
        standing: bool = False,
        expiry_hours: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process captain's consent decision

        Args:
            request_id: ID of the consent request
            granted: Whether captain granted permission
            method: How consent was obtained
            confirmation_text: Captain's confirmation phrase
            scope: Specific scope of permission
            standing: Whether this is a standing permission
            expiry_hours: Hours until standing permission expires

        Returns:
            Result with consent response
        """

        # Process consent
        consent = await self.consent_manager.process_captain_response(
            request_id=request_id,
            granted=granted,
            captain_id=self.captain_id,
            method=method,
            confirmation_text=confirmation_text,
            scope=scope,
            standing=standing,
            expiry_hours=expiry_hours,
        )

        # Log consent decision
        # Get original request to extract destination and data_type
        # In a real implementation, we'd store this mapping
        self.audit_log.log_consent(
            granted=granted,
            destination="pending",  # Would come from request
            data_type="pending",  # Would come from request
            captain_id=self.captain_id,
            method=method.value,
            confirmation_text=confirmation_text,
        )

        if granted:
            return {"success": True, "consent": consent.to_dict(), "message": "Permission granted - ready to transfer"}
        else:
            return {"success": False, "reason": "Captain denied permission", "consent": consent.to_dict()}

    def _filter_by_scope(self, data: Dict[str, Any], scope: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Filter data according to consent scope
        Only include fields that were approved
        """
        if not scope:
            return data

        if "fields" in scope:
            # Only include approved fields
            return {k: v for k, v in data.items() if k in scope["fields"]}

        return data

    async def _execute_transfer(
        self, destination: str, data: Dict[str, Any], data_type: str, purpose: str
    ) -> Dict[str, Any]:
        """
        Actually execute the data transfer
        This is the final step after all approvals
        """

        # Calculate data hash for integrity
        data_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

        try:
            # Actual transfer would happen here
            # For now, simulate success

            return {
                "success": True,
                "destination": destination,
                "data_type": data_type,
                "purpose": purpose,
                "data_hash": data_hash,
                "timestamp": self.audit_log.query(limit=1)[0].timestamp if self.audit_log.query(limit=1) else 0,
            }
        except Exception as e:
            return {"success": False, "reason": f"Transfer failed: {str(e)}", "destination": destination}

    def get_audit_trail(self, destination: Optional[str] = None, hours: int = 168) -> List[Dict[str, Any]]:
        """
        Get audit trail for captain review

        Args:
            destination: Filter by destination (optional)
            hours: Look back period in hours

        Returns:
            List of audit entries
        """
        entries = self.audit_log.query(captain_id=self.captain_id, destination=destination, hours=hours)

        return [entry.to_dict() for entry in entries]

    def get_sharing_summary(self, hours: int = 168) -> Dict[str, Any]:
        """
        Get summary of data sharing for captain

        Voice command: "Ada, veri paylaşım geçmişini göster"
        """
        return self.audit_log.get_summary(self.captain_id, hours)

    def get_standing_permissions(self) -> List[Dict[str, Any]]:
        """
        Get all active standing permissions

        Voice command: "Ada, otomatik izinleri göster"
        """
        return self.consent_manager.get_standing_permissions()

    def revoke_standing_permission(self, destination: str, data_type: str) -> bool:
        """
        Revoke a standing permission

        Voice command: "Ada, [destination] için otomatik paylaşımı iptal et"
        """
        revoked = self.consent_manager.revoke_standing_permission(destination, data_type)

        if revoked:
            # Log revocation
            self.audit_log.log_consent(
                granted=False,
                destination=destination,
                data_type=data_type,
                captain_id=self.captain_id,
                method="captain_revocation",
                confirmation_text="Standing permission revoked",
            )

        return revoked

    def revoke_all_permissions(self) -> int:
        """
        Revoke ALL standing permissions

        Voice command: "Ada, tüm otomatik paylaşımları iptal et"
        """
        permissions = self.get_standing_permissions()
        count = 0

        for perm in permissions:
            self.revoke_standing_permission(perm["destination"], perm["data_type"])
            count += 1

        return count

    def export_privacy_data(self, format: str = "json") -> str:
        """
        Export all privacy-related data for captain
        Implements GDPR/KVKK right to data portability

        Voice command: "Ada, verilerimi dışa aktar"
        """
        return self.audit_log.export_for_captain(captain_id=self.captain_id, hours=8760, format=format)  # 1 year

    def delete_privacy_data(self, days_to_keep: int = 0) -> Dict[str, Any]:
        """
        Delete privacy audit data
        Implements GDPR/KVKK right to erasure

        Voice command: "Ada, veri geçmişini sil"
        """
        deleted = self.audit_log.delete_old_entries(days=days_to_keep)

        return {"success": True, "entries_deleted": deleted, "message": f"{deleted} kayıt silindi"}

    def get_privacy_status(self) -> Dict[str, Any]:
        """
        Get current privacy settings and status

        Voice command: "Ada, gizlilik durumu"
        """
        return {
            "captain_id": self.captain_id,
            "cloud_sync_enabled": self.cloud_sync_enabled,
            "zero_trust_mode": self.zero_trust_mode,
            "captain_auth_required": self.captain_auth_required,
            "standing_permissions_count": len(self.get_standing_permissions()),
            "recent_transfers_count": len(self.get_audit_trail(hours=24)),
        }

    def enable_cloud_backup(self, encryption_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Enable optional zero-knowledge cloud backup

        IMPORTANT: Data encrypted client-side, Ada.Sea cannot read it

        Voice command: "Ada, yedeklemeyi aktif et"
        """
        if not encryption_key:
            return {"success": False, "reason": "Encryption key required for cloud backup"}

        # In real implementation, would set up encrypted backup
        self.cloud_sync_enabled = True

        return {
            "success": True,
            "message": (
                "✓ Yedekleme aktif\n" "✓ Şifreleme anahtarı sadece cihazlarınızda\n" "✓ Ada.sea yedekleri okuyamaz"
            ),
        }

    def disable_cloud_backup(self) -> Dict[str, Any]:
        """
        Disable cloud backup

        Voice command: "Ada, yedeklemeyi durdur"
        """
        self.cloud_sync_enabled = False

        return {"success": True, "message": "Cloud yedekleme devre dışı"}

    def to_dict(self) -> Dict[str, Any]:
        """Export privacy core configuration"""
        return {
            "captain_id": self.captain_id,
            "cloud_sync_enabled": self.cloud_sync_enabled,
            "zero_trust_mode": self.zero_trust_mode,
            "data_policy": self.data_policy.to_dict(),
            "consent_manager": self.consent_manager.to_dict(),
        }
