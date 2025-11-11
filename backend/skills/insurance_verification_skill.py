"""
Insurance Verification Skill - Article E.2.1 Compliance

Verifies yacht insurance coverage per marina regulations:
- Third-Party Financial Liability Insurance required
- Coverage amount must meet marina requirements
- Insurance must be from reputable provider
- Policy must be valid and not expired
- Documentation must be provided before mooring permission
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

try:
    from .base_skill import BaseSkill, SkillMetadata
    from ..database.models import Insurance, InsuranceStatus, InsuranceType
    from ..logger import setup_logger
except ImportError:
    from base_skill import BaseSkill, SkillMetadata
    from database.models import Insurance, InsuranceStatus, InsuranceType
    from logger import setup_logger


logger = setup_logger(__name__)


class InsuranceVerificationSkill(BaseSkill):
    """
    Insurance Verification Skill for Article E.2.1 Compliance

    Article E.2.1: "The Yacht which shall benefit from the Marina is to be
    covered under an applicable Third-Party Financial Liability insurance
    in an amount to be determined by the Company. Such insurance must be
    provided by a prestigious insurance company and the Yacht Owner must
    deliver a copy of the insurance policy to the Company before the issue
    of any certificate of permission."
    """

    def __init__(self):
        super().__init__()
        # In-memory storage (would be database in production)
        self.insurances: Dict[str, Insurance] = {}
        self.min_coverage_amount = 1000000  # 1M EUR minimum
        self.approved_providers = [
            "Allianz", "AXA", "Zurich", "Lloyd's of London",
            "Chartis", "Sompo", "AIG", "Generali"
        ]

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="insurance_verification",
            description="Verify yacht insurance compliance per Article E.2.1 - Third-Party Liability coverage",
            version="1.0.0",
            author="Ada Maritime AI - VERIFY Agent",
            requires_database=True
        )

    async def execute(self, params: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """Execute insurance verification operation"""
        operation = params.get("operation", "verify")

        if operation == "verify":
            return await self._verify_insurance(params, context)
        elif operation == "register":
            return await self._register_insurance(params, context)
        elif operation == "check_expiry":
            return await self._check_expiry(params, context)
        elif operation == "get_status":
            return await self._get_status(params, context)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    async def _verify_insurance(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Verify insurance coverage for a vessel

        Required params:
        - vessel_name: Name of the yacht
        - vessel_registration: Registration number
        - marina_id: Marina where vessel wants to moor
        - booking_id (optional): Associated booking ID
        """
        vessel_name = params.get("vessel_name")
        vessel_registration = params.get("vessel_registration")
        marina_id = params.get("marina_id")
        booking_id = params.get("booking_id")

        if not vessel_name or not vessel_registration:
            return {
                "success": False,
                "insurance_valid": False,
                "error": "vessel_name and vessel_registration are required"
            }

        logger.info(f"Verifying insurance for vessel: {vessel_name} ({vessel_registration})")

        # Check if insurance record exists
        insurance = self._find_insurance_by_vessel(vessel_registration)

        if not insurance:
            logger.warning(f"No insurance record found for vessel: {vessel_registration}")
            return {
                "success": True,
                "insurance_valid": False,
                "insurance_found": False,
                "vessel_name": vessel_name,
                "vessel_registration": vessel_registration,
                "violations": [
                    "No insurance record on file",
                    "Article E.2.1 violation: Insurance policy copy not provided"
                ],
                "required_actions": [
                    "Submit valid Third-Party Liability Insurance policy",
                    "Minimum coverage: EUR 1,000,000",
                    "Must be from approved insurance provider",
                    "Policy must not be expired"
                ],
                "marina_entry_permitted": False
            }

        # Verify insurance validity
        is_valid = insurance.is_valid()
        coverage_adequate = insurance.coverage_amount >= self.min_coverage_amount
        provider_approved = insurance.provider in self.approved_providers
        has_document = insurance.document_url is not None

        violations = []
        if not is_valid:
            if insurance.status == "expired":
                violations.append("Insurance policy has expired")
            elif insurance.status == "rejected":
                violations.append("Insurance policy was rejected")
            elif insurance.status == "pending":
                violations.append("Insurance verification pending")
            else:
                violations.append("Insurance policy is not valid")

        if not coverage_adequate:
            violations.append(
                f"Coverage amount {insurance.coverage_amount} {insurance.currency} "
                f"is below minimum requirement of EUR 1,000,000"
            )

        if not provider_approved:
            violations.append(
                f"Insurance provider '{insurance.provider}' is not on approved list"
            )

        if not has_document:
            violations.append("Insurance policy document not provided")

        # Check expiry date
        days_until_expiry = insurance.days_until_expiry()
        expiry_warning = None
        if 0 < days_until_expiry <= 30:
            expiry_warning = f"Insurance expires in {days_until_expiry} days - renewal required"

        insurance_valid = (
            is_valid and
            coverage_adequate and
            provider_approved and
            has_document
        )

        result = {
            "success": True,
            "insurance_valid": insurance_valid,
            "insurance_found": True,
            "vessel_name": vessel_name,
            "vessel_registration": vessel_registration,
            "marina_entry_permitted": insurance_valid,
            "insurance_details": {
                "insurance_id": insurance.insurance_id,
                "policy_number": insurance.policy_number,
                "provider": insurance.provider,
                "insurance_type": insurance.insurance_type,
                "coverage_amount": insurance.coverage_amount,
                "currency": insurance.currency,
                "issue_date": insurance.issue_date,
                "expiry_date": insurance.expiry_date,
                "days_until_expiry": days_until_expiry,
                "status": insurance.status,
                "verified_by": insurance.verified_by,
                "verified_at": insurance.verified_at
            },
            "compliance_checks": {
                "is_valid": is_valid,
                "coverage_adequate": coverage_adequate,
                "provider_approved": provider_approved,
                "document_provided": has_document
            },
            "violations": violations,
            "warnings": [expiry_warning] if expiry_warning else []
        }

        if not insurance_valid:
            result["required_actions"] = [
                "Resolve all violations listed above",
                "Contact marina administration for assistance",
                "Provide valid insurance documentation"
            ]

        logger.info(
            f"Insurance verification complete for {vessel_name}: "
            f"Valid={insurance_valid}, Violations={len(violations)}"
        )

        return result

    async def _register_insurance(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Register new insurance policy for a vessel

        Required params:
        - vessel_name, vessel_registration, policy_number, insurance_type,
          provider, coverage_amount, currency, issue_date, expiry_date
        """
        required = [
            "vessel_name", "vessel_registration", "policy_number",
            "insurance_type", "provider", "coverage_amount",
            "currency", "issue_date", "expiry_date"
        ]
        self.validate_params(params, required)

        logger.info(f"Registering insurance for vessel: {params['vessel_name']}")

        # Create insurance record
        insurance = Insurance(
            insurance_id=str(uuid.uuid4()),
            vessel_name=params["vessel_name"],
            vessel_registration=params["vessel_registration"],
            booking_id=params.get("booking_id"),
            policy_number=params["policy_number"],
            insurance_type=params["insurance_type"],
            provider=params["provider"],
            coverage_amount=float(params["coverage_amount"]),
            currency=params["currency"],
            issue_date=params["issue_date"],
            expiry_date=params["expiry_date"],
            status="pending",  # Pending verification
            document_url=params.get("document_url"),
            notes=params.get("notes"),
            marina_id=params.get("marina_id")
        )

        # Store insurance record
        self.insurances[insurance.insurance_id] = insurance

        # Verify if it meets requirements
        is_adequate = (
            insurance.coverage_amount >= self.min_coverage_amount and
            insurance.provider in self.approved_providers
        )

        # Auto-approve if adequate and has document
        if is_adequate and insurance.document_url:
            insurance.status = "valid"
            insurance.verified_at = datetime.now().isoformat()
            insurance.verified_by = "auto_verify_system"

        logger.info(
            f"Insurance registered: {insurance.insurance_id}, Status: {insurance.status}"
        )

        return {
            "success": True,
            "insurance_id": insurance.insurance_id,
            "status": insurance.status,
            "auto_verified": insurance.status == "valid",
            "coverage_adequate": is_adequate,
            "message": "Insurance policy registered successfully",
            "next_steps": [
                "Upload insurance policy document if not provided",
                "Wait for manual verification if auto-verification failed",
                "Monitor expiry date for renewal"
            ] if insurance.status != "valid" else []
        }

    async def _check_expiry(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Check insurance policies nearing expiry

        Optional params:
        - marina_id: Filter by marina
        - days_threshold: Days before expiry to flag (default: 30)
        """
        marina_id = params.get("marina_id")
        days_threshold = params.get("days_threshold", 30)

        logger.info(f"Checking insurance expiry for marina: {marina_id or 'all'}")

        expiring_soon = []
        expired = []

        for insurance in self.insurances.values():
            if marina_id and insurance.marina_id != marina_id:
                continue

            days_left = insurance.days_until_expiry()

            if days_left < 0:
                expired.append({
                    "insurance_id": insurance.insurance_id,
                    "vessel_name": insurance.vessel_name,
                    "vessel_registration": insurance.vessel_registration,
                    "policy_number": insurance.policy_number,
                    "expired_days_ago": abs(days_left),
                    "expiry_date": insurance.expiry_date
                })
            elif 0 <= days_left <= days_threshold:
                expiring_soon.append({
                    "insurance_id": insurance.insurance_id,
                    "vessel_name": insurance.vessel_name,
                    "vessel_registration": insurance.vessel_registration,
                    "policy_number": insurance.policy_number,
                    "days_until_expiry": days_left,
                    "expiry_date": insurance.expiry_date
                })

        logger.info(
            f"Expiry check: {len(expired)} expired, "
            f"{len(expiring_soon)} expiring within {days_threshold} days"
        )

        return {
            "success": True,
            "marina_id": marina_id,
            "days_threshold": days_threshold,
            "expired_count": len(expired),
            "expiring_soon_count": len(expiring_soon),
            "expired_policies": expired,
            "expiring_soon_policies": expiring_soon,
            "requires_immediate_action": len(expired) > 0,
            "recommended_actions": [
                f"Contact {len(expired)} vessels with expired insurance immediately",
                f"Send renewal reminders to {len(expiring_soon)} vessels",
                "Restrict marina access for vessels with expired insurance per Article E.2.1"
            ] if (expired or expiring_soon) else []
        }

    async def _get_status(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Get insurance status for a vessel or all vessels

        Optional params:
        - vessel_registration: Get status for specific vessel
        - marina_id: Filter by marina
        """
        vessel_registration = params.get("vessel_registration")
        marina_id = params.get("marina_id")

        if vessel_registration:
            insurance = self._find_insurance_by_vessel(vessel_registration)
            if not insurance:
                return {
                    "success": True,
                    "found": False,
                    "vessel_registration": vessel_registration,
                    "message": "No insurance record found"
                }

            return {
                "success": True,
                "found": True,
                "insurance": {
                    "insurance_id": insurance.insurance_id,
                    "vessel_name": insurance.vessel_name,
                    "vessel_registration": insurance.vessel_registration,
                    "policy_number": insurance.policy_number,
                    "provider": insurance.provider,
                    "coverage_amount": insurance.coverage_amount,
                    "currency": insurance.currency,
                    "status": insurance.status,
                    "is_valid": insurance.is_valid(),
                    "expiry_date": insurance.expiry_date,
                    "days_until_expiry": insurance.days_until_expiry()
                }
            }

        # Get summary for all vessels
        insurances = list(self.insurances.values())
        if marina_id:
            insurances = [i for i in insurances if i.marina_id == marina_id]

        valid = len([i for i in insurances if i.is_valid()])
        expired = len([i for i in insurances if i.status == "expired" or i.days_until_expiry() < 0])
        pending = len([i for i in insurances if i.status == "pending"])

        return {
            "success": True,
            "marina_id": marina_id,
            "total_insurances": len(insurances),
            "by_status": {
                "valid": valid,
                "expired": expired,
                "pending": pending
            },
            "compliance_rate": round((valid / len(insurances) * 100) if insurances else 0, 2)
        }

    def _find_insurance_by_vessel(self, vessel_registration: str) -> Optional[Insurance]:
        """Find insurance record by vessel registration"""
        for insurance in self.insurances.values():
            if insurance.vessel_registration == vessel_registration:
                return insurance
        return None
