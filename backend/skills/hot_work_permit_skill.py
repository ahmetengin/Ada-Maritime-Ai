"""
Hot Work Permit Monitoring Skill - Article E.5.5 Compliance

Monitors hot work activities per marina safety regulations:
- Hot works: welding, grinding, sanding, scraping, paint, varnish
- All necessary safety measures must be in place
- Fire watch required
- Safety equipment must be present
- Work interrupted immediately if violations detected
- Protective measures for nearby yachts and facilities
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

try:
    from .base_skill import BaseSkill, SkillMetadata
    from ..database.models import Permit, PermitStatus, PermitType
    from ..logger import setup_logger
except ImportError:
    from base_skill import BaseSkill, SkillMetadata
    from database.models import Permit, PermitStatus, PermitType
    from logger import setup_logger


logger = setup_logger(__name__)


class HotWorkPermitSkill(BaseSkill):
    """
    Hot Work Permit Monitoring Skill for Article E.5.5 Compliance

    Article E.5.5: "During any hot works organized by the Yacht Owner such as
    wood, paint, varnish, welding, grinding, sanding, scraping, etc. on board,
    all necessary measures must be taken to prevent other yachts and facilities
    from being polluted and damaged. Any works which are found to be performed
    without any such measures taken shall be interrupted by the Company. Any
    damages shall be ascertained via a detailed report and the total damages
    shall be immediately indemnified by the Yacht Owner who is at fault."
    """

    def __init__(self):
        super().__init__()
        # In-memory storage (would be database in production)
        self.permits: Dict[str, Permit] = {}

        # Hot work types
        self.hot_work_types = [
            "welding", "grinding", "sanding", "scraping",
            "painting", "varnishing", "heat_treatment",
            "cutting", "brazing", "soldering"
        ]

        # Required safety equipment for hot work
        self.required_safety_equipment = [
            "fire_extinguisher",
            "fire_blanket",
            "safety_goggles",
            "protective_gloves",
            "ventilation_equipment",
            "spark_shields"
        ]

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="hot_work_monitoring",
            description="Monitor hot work permits and safety compliance per Article E.5.5",
            version="1.0.0",
            author="Ada Maritime AI - VERIFY Agent",
            requires_database=True
        )

    async def execute(self, params: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """Execute hot work permit operation"""
        operation = params.get("operation", "monitor")

        if operation == "request":
            return await self._request_permit(params, context)
        elif operation == "approve":
            return await self._approve_permit(params, context)
        elif operation == "monitor":
            return await self._monitor_permit(params, context)
        elif operation == "complete":
            return await self._complete_permit(params, context)
        elif operation == "check_active":
            return await self._check_active_permits(params, context)
        elif operation == "violation_check":
            return await self._check_violations(params, context)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    async def _request_permit(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Request a hot work permit

        Required params:
        - marina_id, work_description, work_location,
          scheduled_start, scheduled_end, requested_by,
          requester_email, requester_phone
        """
        required = [
            "marina_id", "work_description", "work_location",
            "scheduled_start", "scheduled_end", "requested_by",
            "requester_email", "requester_phone"
        ]
        self.validate_params(params, required)

        logger.info(f"Hot work permit requested by: {params['requested_by']}")

        # Determine if work is hot work
        work_desc_lower = params["work_description"].lower()
        is_hot_work = any(hw_type in work_desc_lower for hw_type in self.hot_work_types)

        # Create permit
        permit = Permit(
            permit_id=str(uuid.uuid4()),
            permit_type="hot_work" if is_hot_work else "cold_work",
            marina_id=params["marina_id"],
            berth_id=params.get("berth_id"),
            vessel_name=params.get("vessel_name"),
            vessel_registration=params.get("vessel_registration"),
            requested_by=params["requested_by"],
            requester_email=params["requester_email"],
            requester_phone=params["requester_phone"],
            work_description=params["work_description"],
            work_location=params["work_location"],
            requested_at=datetime.now().isoformat(),
            scheduled_start=params["scheduled_start"],
            scheduled_end=params["scheduled_end"],
            status="requested",
            fire_watch_required=is_hot_work,  # Hot work always requires fire watch
            safety_zone_meters=params.get("safety_zone_meters", 5.0 if is_hot_work else None),
            notes=params.get("notes")
        )

        # Determine required safety equipment based on work type
        if is_hot_work:
            permit.safety_equipment_required = self.required_safety_equipment.copy()

            # Add specific conditions for hot work
            permit.conditions = [
                "Fire watch must be present during all work",
                "Work must stop immediately if unsafe conditions detected",
                "Nearby vessels must be notified and protected",
                "Fire extinguisher must be within 3 meters of work area",
                "No flammable materials within safety zone",
                "Spark shields must be properly positioned"
            ]

        # Store permit
        self.permits[permit.permit_id] = permit

        logger.info(
            f"Permit {permit.permit_id} created: Type={permit.permit_type}, "
            f"Status={permit.status}"
        )

        return {
            "success": True,
            "permit_id": permit.permit_id,
            "permit_type": permit.permit_type,
            "status": permit.status,
            "is_hot_work": is_hot_work,
            "fire_watch_required": permit.fire_watch_required,
            "safety_zone_meters": permit.safety_zone_meters,
            "safety_equipment_required": permit.safety_equipment_required,
            "conditions": permit.conditions,
            "message": "Hot work permit request submitted" if is_hot_work else "Work permit request submitted",
            "next_steps": [
                "Wait for marina management approval",
                "Prepare all required safety equipment",
                "Assign fire watch personnel (if hot work)",
                "Notify nearby vessels",
                "Review safety conditions and procedures"
            ],
            "estimated_approval_time": "2-4 hours for standard requests"
        }

    async def _approve_permit(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Approve a hot work permit

        Required params:
        - permit_id, approved_by
        """
        permit_id = params.get("permit_id")
        approved_by = params.get("approved_by")

        if not permit_id or not approved_by:
            return {
                "success": False,
                "error": "permit_id and approved_by are required"
            }

        if permit_id not in self.permits:
            return {
                "success": False,
                "error": f"Permit {permit_id} not found"
            }

        permit = self.permits[permit_id]

        # Check if permit can be approved
        if permit.status not in ["requested", "rejected"]:
            return {
                "success": False,
                "error": f"Permit cannot be approved from status: {permit.status}"
            }

        # Approve permit
        permit.status = "approved"
        permit.approved_by = approved_by
        permit.approved_at = datetime.now().isoformat()

        # If fire watch required, ensure it's assigned
        if permit.fire_watch_required and not permit.fire_watch_personnel:
            permit.conditions.append(
                "CRITICAL: Fire watch personnel must be assigned before work begins"
            )

        logger.info(f"Permit {permit_id} approved by {approved_by}")

        return {
            "success": True,
            "permit_id": permit_id,
            "status": permit.status,
            "approved_by": approved_by,
            "approved_at": permit.approved_at,
            "message": "Permit approved successfully",
            "important_reminders": [
                "Ensure all safety equipment is in place before starting",
                "Fire watch must be present for entire duration (if required)",
                "Work must be within scheduled time window",
                "Report any incidents or violations immediately",
                "Complete permit when work is finished"
            ],
            "work_can_begin": not permit.fire_watch_required or bool(permit.fire_watch_personnel)
        }

    async def _monitor_permit(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Monitor active hot work permit for compliance

        Required params:
        - permit_id
        """
        permit_id = params.get("permit_id")

        if not permit_id:
            return {
                "success": False,
                "error": "permit_id is required"
            }

        if permit_id not in self.permits:
            return {
                "success": False,
                "error": f"Permit {permit_id} not found"
            }

        permit = self.permits[permit_id]

        logger.info(f"Monitoring permit: {permit_id}")

        # Check compliance
        violations = []
        warnings = []

        # Check if permit is active
        is_active = permit.is_active()
        is_expired = permit.is_expired()

        if is_expired:
            violations.append("Permit has expired - work must stop immediately")

        if permit.status == "active" and not is_active:
            violations.append("Work is outside scheduled time window")

        # Check fire watch for hot work
        if permit.permit_type == "hot_work":
            if not permit.fire_watch_personnel:
                violations.append("CRITICAL: No fire watch assigned for hot work - Article E.5.5 violation")

            if permit.fire_watch_required and permit.status == "active":
                # In production, would verify fire watch is actually present
                warnings.append("Verify fire watch is present at work location")

        # Check safety zone
        if permit.safety_zone_meters:
            warnings.append(f"Ensure {permit.safety_zone_meters}m safety zone is maintained")

        # Check if work is logged as completed
        if permit.status == "active" and is_expired:
            violations.append("Work did not complete within scheduled time - status update required")

        # Compliance status
        is_compliant = len(violations) == 0

        result = {
            "success": True,
            "permit_id": permit_id,
            "permit_type": permit.permit_type,
            "status": permit.status,
            "is_compliant": is_compliant,
            "is_active": is_active,
            "is_expired": is_expired,
            "permit_details": {
                "work_description": permit.work_description,
                "work_location": permit.work_location,
                "scheduled_start": permit.scheduled_start,
                "scheduled_end": permit.scheduled_end,
                "vessel_name": permit.vessel_name,
                "berth_id": permit.berth_id,
                "fire_watch_personnel": permit.fire_watch_personnel,
                "safety_zone_meters": permit.safety_zone_meters
            },
            "violations": violations,
            "warnings": warnings,
            "required_actions": []
        }

        if violations:
            result["required_actions"] = [
                "Stop work immediately if critical violations exist",
                "Contact marina management",
                "Address all violations before resuming work",
                "Document all incidents per Article E.5.5"
            ]

            # Mark permit as having violation
            permit.violation_logged = True

            logger.warning(
                f"Permit {permit_id} has {len(violations)} violations: {violations}"
            )
        else:
            logger.info(f"Permit {permit_id} is compliant")

        return result

    async def _complete_permit(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Mark permit as completed

        Required params:
        - permit_id
        """
        permit_id = params.get("permit_id")

        if not permit_id:
            return {
                "success": False,
                "error": "permit_id is required"
            }

        if permit_id not in self.permits:
            return {
                "success": False,
                "error": f"Permit {permit_id} not found"
            }

        permit = self.permits[permit_id]

        if permit.status == "completed":
            return {
                "success": True,
                "permit_id": permit_id,
                "message": "Permit is already marked as completed"
            }

        # Mark as completed
        permit.status = "completed"
        permit.completed_at = datetime.now().isoformat()

        logger.info(f"Permit {permit_id} marked as completed")

        return {
            "success": True,
            "permit_id": permit_id,
            "status": permit.status,
            "completed_at": permit.completed_at,
            "violations_logged": permit.violation_logged,
            "message": "Hot work permit completed successfully" if permit.permit_type == "hot_work" else "Work permit completed",
            "post_work_requirements": [
                "Clean work area thoroughly",
                "Remove all equipment and materials",
                "Verify no fire hazards remain",
                "Report any incidents or damages",
                "File completion report with marina management"
            ] if permit.permit_type == "hot_work" else []
        }

    async def _check_active_permits(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Check all active permits in a marina

        Optional params:
        - marina_id: Filter by marina
        """
        marina_id = params.get("marina_id")

        active_permits = []
        expired_permits = []
        pending_approval = []

        for permit in self.permits.values():
            if marina_id and permit.marina_id != marina_id:
                continue

            if permit.status == "requested":
                pending_approval.append({
                    "permit_id": permit.permit_id,
                    "permit_type": permit.permit_type,
                    "requested_by": permit.requested_by,
                    "requested_at": permit.requested_at,
                    "work_description": permit.work_description[:100]
                })
            elif permit.is_active():
                active_permits.append({
                    "permit_id": permit.permit_id,
                    "permit_type": permit.permit_type,
                    "work_location": permit.work_location,
                    "vessel_name": permit.vessel_name,
                    "fire_watch_personnel": permit.fire_watch_personnel,
                    "scheduled_end": permit.scheduled_end
                })
            elif permit.is_expired() and permit.status == "active":
                expired_permits.append({
                    "permit_id": permit.permit_id,
                    "permit_type": permit.permit_type,
                    "work_location": permit.work_location,
                    "scheduled_end": permit.scheduled_end
                })

        logger.info(
            f"Active permits check: {len(active_permits)} active, "
            f"{len(expired_permits)} expired, {len(pending_approval)} pending"
        )

        return {
            "success": True,
            "marina_id": marina_id,
            "timestamp": datetime.now().isoformat(),
            "active_permits_count": len(active_permits),
            "expired_permits_count": len(expired_permits),
            "pending_approval_count": len(pending_approval),
            "active_permits": active_permits,
            "expired_permits": expired_permits,
            "pending_approval": pending_approval,
            "requires_attention": len(expired_permits) > 0
        }

    async def _check_violations(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Check for permit violations across marina

        Optional params:
        - marina_id: Filter by marina
        """
        marina_id = params.get("marina_id")

        violations_found = []

        for permit in self.permits.values():
            if marina_id and permit.marina_id != marina_id:
                continue

            # Skip completed permits
            if permit.status == "completed":
                continue

            issues = []

            # Check if hot work without approval
            if permit.permit_type == "hot_work" and permit.status == "requested":
                issues.append("Hot work permit not yet approved")

            # Check fire watch assignment
            if permit.permit_type == "hot_work" and not permit.fire_watch_personnel:
                issues.append("No fire watch assigned for hot work - Article E.5.5 violation")

            # Check if active but expired
            if permit.status == "active" and permit.is_expired():
                issues.append("Permit expired but status still active")

            if issues:
                violations_found.append({
                    "permit_id": permit.permit_id,
                    "permit_type": permit.permit_type,
                    "vessel_name": permit.vessel_name,
                    "work_location": permit.work_location,
                    "status": permit.status,
                    "violations": issues
                })

        logger.info(f"Violation check: {len(violations_found)} permits with violations")

        return {
            "success": True,
            "marina_id": marina_id,
            "timestamp": datetime.now().isoformat(),
            "violations_count": len(violations_found),
            "violations": violations_found,
            "critical_violations": [
                v for v in violations_found
                if any("CRITICAL" in issue or "Article E.5.5" in issue for issue in v["violations"])
            ],
            "requires_immediate_action": len(violations_found) > 0
        }
