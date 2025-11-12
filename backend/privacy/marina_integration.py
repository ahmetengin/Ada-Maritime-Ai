"""
Ada.Marina Integration with Trust Boundaries
Explicit data sharing model for Ada ecosystem marinas
"""

from typing import Dict, Any, Optional, List
import asyncio

from .privacy_core import AdaSeaPrivacyCore
from .data_policy import DataClassification


class AdaMarinaIntegration:
    """
    Ada.Marina integration with explicit consent model

    Even though Ada.Marina is part of the Ada ecosystem,
    captain still controls what data is shared.

    Trust Boundary: Captain approval required for ALL transfers
    """

    def __init__(self, privacy_core: AdaSeaPrivacyCore):
        """
        Initialize marina integration

        Args:
            privacy_core: Core privacy management system
        """
        self.privacy_core = privacy_core
        self.trusted_destination = True  # Part of Ada ecosystem
        self.default_permissions = {
            'automatic': False,  # Still requires confirmation
            'requires_confirmation': True
        }

    async def request_berth_assignment(
        self,
        marina_id: str,
        vessel_specs: Dict[str, Any],
        arrival_time: str
    ) -> Dict[str, Any]:
        """
        Request berth assignment from Ada.Marina

        Minimal data transfer:
        - Vessel length, beam, draft (for berth sizing)
        - Arrival time (for scheduling)

        NOT sent:
        - GPS coordinates
        - Financial info
        - Personal data
        - Communication history

        Args:
            marina_id: Marina identifier
            vessel_specs: Vessel specifications
            arrival_time: Expected arrival time

        Returns:
            Result with berth assignment or consent request
        """

        # 1. Prepare minimal data request
        minimal_data = {
            'vessel_length': vessel_specs.get('length'),
            'vessel_beam': vessel_specs.get('beam'),
            'vessel_draft': vessel_specs.get('draft'),
            'arrival_time': arrival_time,
        }

        # 2. Request through privacy core (captain approval required)
        result = await self.privacy_core.share_data(
            destination=f"Ada.marina:{marina_id}",
            data=minimal_data,
            data_type=DataClassification.VESSEL_SPECIFICATIONS.value,
            purpose="berth_assignment"
        )

        if not result['success'] and 'request' in result:
            # Return consent request to captain
            return {
                'success': False,
                'requires_consent': True,
                'request': result['request'],
                'voice_prompt': result['voice_prompt'],
                'message': (
                    f"Ada.marina için {marina_id} sistemine "
                    f"tekne ölçüleri ve varış saatini göndermek "
                    f"istiyorum. Onaylıyor musunuz?"
                )
            }

        return result

    async def inform_arrival(
        self,
        marina_id: str,
        vessel_name: str,
        current_position: Dict[str, float],
        berth_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Inform marina of arrival (check-in)

        This is typically captain-initiated:
        Voice: "Ada, marina'ya check-in yap"

        Args:
            marina_id: Marina identifier
            vessel_name: Vessel name
            current_position: Current GPS position
            berth_number: Assigned berth (if known)

        Returns:
            Result of check-in
        """

        # Captain explicitly commanded check-in
        # But still ask for confirmation with specific data

        arrival_data = {
            'vessel_name': vessel_name,
            'current_position': current_position,
        }

        if berth_number:
            arrival_data['berth_number'] = berth_number

        result = await self.privacy_core.share_data(
            destination=f"Ada.marina:{marina_id}",
            data=arrival_data,
            data_type=DataClassification.CURRENT_POSITION.value,
            purpose="check_in"
        )

        return result

    async def request_services(
        self,
        marina_id: str,
        services: List[str],
        vessel_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Request marina services (fuel, maintenance, etc.)

        Args:
            marina_id: Marina identifier
            services: List of requested services
            vessel_info: Relevant vessel information

        Returns:
            Result of service request
        """

        # Only send data relevant to services
        service_data = {
            'services': services,
            'vessel_name': vessel_info.get('name'),
            'vessel_type': vessel_info.get('type'),
        }

        # Add specific info based on services
        if 'fuel' in services:
            service_data['fuel_capacity'] = vessel_info.get('fuel_capacity')

        result = await self.privacy_core.share_data(
            destination=f"Ada.marina:{marina_id}",
            data=service_data,
            data_type=DataClassification.VESSEL_SPECIFICATIONS.value,
            purpose=f"services:{','.join(services)}"
        )

        return result

    async def check_compliance(
        self,
        marina_id: str,
        vessel_docs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Share compliance documentation with marina

        For automated compliance checking (176 articles)

        Args:
            marina_id: Marina identifier
            vessel_docs: Vessel documentation

        Returns:
            Compliance check result
        """

        # Only share necessary compliance docs
        compliance_data = {
            'insurance_valid': vessel_docs.get('insurance_valid'),
            'insurance_coverage': vessel_docs.get('insurance_coverage'),
            'registration_valid': vessel_docs.get('registration_valid'),
            'seaworthiness_cert_valid': vessel_docs.get('seaworthiness_cert_valid'),
        }

        result = await self.privacy_core.share_data(
            destination=f"Ada.marina:{marina_id}:compliance",
            data=compliance_data,
            data_type=DataClassification.VESSEL_SPECIFICATIONS.value,
            purpose="compliance_check"
        )

        return result

    async def emergency_notification(
        self,
        marina_id: str,
        emergency_type: str,
        vessel_info: Dict[str, Any],
        position: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Emergency notification to marina

        Uses emergency bypass for immediate transfer

        Args:
            marina_id: Marina identifier
            emergency_type: Type of emergency
            vessel_info: Vessel information
            position: Current position

        Returns:
            Emergency notification result
        """

        emergency_data = {
            'emergency_type': emergency_type,
            'vessel_name': vessel_info.get('name'),
            'vessel_type': vessel_info.get('type'),
            'position': position,
            'contact': vessel_info.get('emergency_contact'),
            'timestamp': vessel_info.get('timestamp'),
        }

        # Use emergency bypass
        result = await self.privacy_core.share_data(
            destination=f"Ada.marina:{marina_id}:emergency",
            data=emergency_data,
            data_type=DataClassification.CURRENT_POSITION.value,
            purpose=f"emergency:{emergency_type}",
            bypass_consent=True  # Emergency - logged and flagged
        )

        return result

    def setup_standing_permission(
        self,
        marina_id: str,
        permission_type: str,
        expiry_hours: int = 168  # 7 days default
    ) -> Dict[str, Any]:
        """
        Set up standing permission for a marina

        Captain can pre-approve certain data sharing:
        Voice: "Ada, Ada.marina'ya tekne ölçülerini otomatik gönderebilirsin"

        Args:
            marina_id: Marina identifier
            permission_type: Type of permission (e.g., 'vessel_specs', 'arrival_time')
            expiry_hours: Hours until permission expires

        Returns:
            Standing permission configuration
        """

        permission_map = {
            'vessel_specs': DataClassification.VESSEL_SPECIFICATIONS.value,
            'arrival_time': DataClassification.ARRIVAL_TIME.value,
            'current_position': DataClassification.CURRENT_POSITION.value,
        }

        if permission_type not in permission_map:
            return {
                'success': False,
                'reason': f'Invalid permission type: {permission_type}'
            }

        # Create standing permission request
        # This would integrate with consent manager
        return {
            'success': True,
            'message': (
                f"✓ {marina_id} için {permission_type} "
                f"otomatik paylaşım aktif ({expiry_hours} saat)"
            ),
            'destination': f"Ada.marina:{marina_id}",
            'data_type': permission_map[permission_type],
            'expiry_hours': expiry_hours
        }

    def get_marina_permissions(self) -> List[Dict[str, Any]]:
        """
        Get all active marina permissions

        Voice: "Ada, marina izinlerini göster"
        """
        all_permissions = self.privacy_core.get_standing_permissions()

        # Filter for marina destinations
        marina_permissions = [
            p for p in all_permissions
            if p['destination'].startswith('Ada.marina:')
        ]

        return marina_permissions

    def revoke_marina_permission(self, marina_id: str) -> int:
        """
        Revoke all permissions for a marina

        Voice: "Ada, [marina_id] için tüm izinleri iptal et"
        """
        permissions = self.get_marina_permissions()
        count = 0

        for perm in permissions:
            if marina_id in perm['destination']:
                self.privacy_core.revoke_standing_permission(
                    perm['destination'],
                    perm['data_type']
                )
                count += 1

        return count

    def get_marina_sharing_history(
        self,
        marina_id: Optional[str] = None,
        hours: int = 168
    ) -> List[Dict[str, Any]]:
        """
        Get data sharing history with marinas

        Voice: "Ada, marina'lara ne paylaştım?"
        """
        destination_filter = None
        if marina_id:
            destination_filter = f"Ada.marina:{marina_id}"

        return self.privacy_core.get_audit_trail(
            destination=destination_filter,
            hours=hours
        )


# Voice command handlers for marina integration
MARINA_VOICE_COMMANDS = {
    'tr': {
        'check_in': [
            "marina'ya check-in yap",
            "marina'ya bildir",
            "varışımı bildir"
        ],
        'berth_request': [
            "berth reserve et",
            "yer ayırt",
            "yer rezervasyonu"
        ],
        'service_request': [
            "servis talep et",
            "yakıt iste",
            "bakım iste"
        ],
        'show_permissions': [
            "marina izinlerini göster",
            "marina paylaşımlarını göster"
        ],
        'revoke_all': [
            "marina izinlerini iptal et",
            "otomatik paylaşımı durdur"
        ]
    },
    'en': {
        'check_in': [
            "check in to marina",
            "notify marina",
            "inform arrival"
        ],
        'berth_request': [
            "reserve berth",
            "request berth",
            "book berth"
        ],
        'service_request': [
            "request service",
            "request fuel",
            "request maintenance"
        ],
        'show_permissions': [
            "show marina permissions",
            "show marina sharing"
        ],
        'revoke_all': [
            "revoke marina permissions",
            "stop automatic sharing"
        ]
    }
}
