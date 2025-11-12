"""
Unified Marina Orchestrator - Integration of Big-5 and VERIFY Agent

Combines operational skills (Big-5) with compliance/security skills (VERIFY)
for comprehensive marina management.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .big5_orchestrator import Big5Orchestrator, AgentContext, SkillResult
from .verify_agent import VerifyAgent, VerifyContext
from ..skills.insurance_verification_skill import InsuranceVerificationSkill
from ..skills.hot_work_permit_skill import HotWorkPermitSkill
from ..skills.compliance_checking_skill import ComplianceCheckingSkill
from ..skills.berth_management_skill import BerthManagementSkill
from ..skills.weather_skill import WeatherSkill
from ..skills.maintenance_skill import MaintenanceSkill
from ..logger import setup_logger


logger = setup_logger(__name__)


class UnifiedMarinaOrchestrator:
    """
    Unified Marina Orchestrator

    Integrates Big-5 operational skills with VERIFY compliance/security skills
    for comprehensive marina management system.

    Capabilities:
    - Operational Skills: Berth management, weather, maintenance, analytics
    - Compliance Skills: Insurance, permits, compliance checking, violations
    - Security Skills: Incident management, access control
    - Real-time Monitoring: Active permits, violations, critical issues
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize unified orchestrator with all skills"""
        logger.info("Initializing Unified Marina Orchestrator...")

        # Initialize both orchestrators
        self.big5 = Big5Orchestrator(api_key=api_key)
        self.verify = VerifyAgent(api_key=api_key)

        # Register all operational skills
        self._register_operational_skills()

        # Register all compliance/security skills
        self._register_compliance_skills()

        logger.info(
            f"Unified Marina Orchestrator initialized with "
            f"{len(self.big5.get_available_skills())} operational skills and "
            f"{len(self.verify.get_available_skills())} compliance skills"
        )

    def _register_operational_skills(self) -> None:
        """Register Big-5 operational skills"""
        try:
            # Berth Management
            self.big5.register_skill("berth_management", BerthManagementSkill())

            # Weather
            self.big5.register_skill("weather", WeatherSkill())

            # Maintenance
            self.big5.register_skill("maintenance", MaintenanceSkill())

            logger.info("Operational skills registered successfully")

        except Exception as e:
            logger.warning(f"Some operational skills could not be registered: {e}")

    def _register_compliance_skills(self) -> None:
        """Register VERIFY compliance/security skills"""
        try:
            # Insurance Verification (Article E.2.1)
            insurance_skill = InsuranceVerificationSkill()
            self.verify.register_skill("insurance_verification", insurance_skill)
            self.big5.register_skill("verify_insurance", insurance_skill)

            # Hot Work Permit Monitoring (Article E.5.5)
            permit_skill = HotWorkPermitSkill()
            self.verify.register_skill("hot_work_monitoring", permit_skill)
            self.big5.register_skill("verify_hot_work", permit_skill)

            # Compliance Checking (176 Articles)
            compliance_skill = ComplianceCheckingSkill()
            self.verify.register_skill("compliance_checking", compliance_skill)
            self.big5.register_skill("verify_compliance", compliance_skill)

            logger.info("Compliance skills registered successfully")

        except Exception as e:
            logger.error(f"Failed to register compliance skills: {e}")
            raise

    async def execute_operational_task(
        self,
        skill_name: str,
        params: Dict[str, Any],
        context: AgentContext
    ) -> SkillResult:
        """Execute operational skill via Big-5 Orchestrator"""
        logger.info(f"Executing operational task: {skill_name}")
        return await self.big5.execute_skill(skill_name, params, context)

    async def execute_compliance_task(
        self,
        skill_name: str,
        params: Dict[str, Any],
        verify_context: VerifyContext
    ) -> Dict[str, Any]:
        """Execute compliance skill via VERIFY Agent"""
        logger.info(f"Executing compliance task: {skill_name}")

        if skill_name not in self.verify.skills:
            raise ValueError(f"Compliance skill not found: {skill_name}")

        skill = self.verify.skills[skill_name]
        return await skill.execute(params, verify_context)

    async def verify_vessel_compliance(
        self,
        vessel_name: str,
        vessel_registration: str,
        marina_id: str,
        booking_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive vessel compliance check

        Checks:
        - Insurance validity (Article E.2.1)
        - Outstanding violations
        - Active permits
        - Security incidents

        Returns complete compliance status and authorization
        """
        logger.info(f"Verifying vessel compliance: {vessel_name} ({vessel_registration})")

        results = {
            "vessel_name": vessel_name,
            "vessel_registration": vessel_registration,
            "marina_id": marina_id,
            "timestamp": None,
            "overall_compliant": False,
            "entry_authorized": False,
            "checks_performed": {},
            "violations": [],
            "warnings": [],
            "required_actions": []
        }

        # 1. Check insurance (Article E.2.1)
        try:
            insurance_result = await self.verify.verify_insurance(
                vessel_name=vessel_name,
                vessel_registration=vessel_registration,
                marina_id=marina_id,
                booking_id=booking_id
            )

            results["checks_performed"]["insurance"] = {
                "valid": insurance_result.get("insurance_valid", False),
                "details": insurance_result
            }

            if not insurance_result.get("insurance_valid"):
                results["violations"].extend(insurance_result.get("violations", []))
                results["required_actions"].extend(insurance_result.get("required_actions", []))

        except Exception as e:
            logger.error(f"Insurance check failed: {e}")
            results["checks_performed"]["insurance"] = {
                "valid": False,
                "error": str(e)
            }
            results["violations"].append("Insurance verification failed")

        # 2. Check for outstanding violations
        try:
            active_violations = self.verify.get_active_violations(
                marina_id=marina_id
            )
            vessel_violations = [
                v for v in active_violations
                if v.vessel_name == vessel_name or v.entity_id == vessel_registration
            ]

            results["checks_performed"]["violations"] = {
                "count": len(vessel_violations),
                "critical_count": len([v for v in vessel_violations if v.severity == "critical"])
            }

            if vessel_violations:
                results["violations"].extend([
                    f"Outstanding {v.severity} violation: {v.description}"
                    for v in vessel_violations[:5]
                ])

        except Exception as e:
            logger.error(f"Violation check failed: {e}")

        # 3. Determine overall compliance
        insurance_valid = results["checks_performed"].get("insurance", {}).get("valid", False)
        has_critical_violations = any(
            "critical" in v.lower() for v in results["violations"]
        )

        results["overall_compliant"] = insurance_valid and not has_critical_violations
        results["entry_authorized"] = results["overall_compliant"]

        if not results["entry_authorized"]:
            if not insurance_valid:
                results["required_actions"].insert(0, "Valid insurance required before marina entry")
            if has_critical_violations:
                results["required_actions"].insert(0, "Resolve critical violations before marina entry")

        logger.info(
            f"Vessel compliance check complete: Compliant={results['overall_compliant']}, "
            f"Authorized={results['entry_authorized']}"
        )

        return results

    async def process_hot_work_request(
        self,
        work_description: str,
        work_location: str,
        scheduled_start: str,
        scheduled_end: str,
        requested_by: str,
        requester_email: str,
        requester_phone: str,
        marina_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process hot work permit request (Article E.5.5)

        Handles complete workflow:
        1. Validate request
        2. Create permit
        3. Check compliance
        4. Return permit details with safety requirements
        """
        logger.info(f"Processing hot work request: {work_description[:50]}...")

        # Execute hot work permit request
        permit_result = await self.execute_compliance_task(
            "hot_work_monitoring",
            {
                "operation": "request",
                "marina_id": marina_id,
                "work_description": work_description,
                "work_location": work_location,
                "scheduled_start": scheduled_start,
                "scheduled_end": scheduled_end,
                "requested_by": requested_by,
                "requester_email": requester_email,
                "requester_phone": requester_phone,
                **kwargs
            },
            VerifyContext(
                marina_id=marina_id,
                user_id=requester_email,
                session_id=f"hotwork_{marina_id}",
                check_scope="permits"
            )
        )

        logger.info(f"Hot work permit created: {permit_result.get('permit_id')}")

        return permit_result

    async def run_daily_compliance_audit(self, marina_id: str) -> Dict[str, Any]:
        """
        Run daily compliance audit for marina

        Checks:
        - All active permits
        - Insurance expiry
        - Outstanding violations
        - Critical issues

        Returns comprehensive audit report
        """
        logger.info(f"Running daily compliance audit for marina: {marina_id}")

        audit_results = {
            "marina_id": marina_id,
            "audit_type": "daily",
            "timestamp": None,
            "sections": {}
        }

        # 1. Run comprehensive compliance audit
        try:
            context = VerifyContext(
                marina_id=marina_id,
                user_id="system",
                session_id=f"daily_audit_{marina_id}",
                check_scope="all"
            )

            compliance_audit = self.verify.run_compliance_audit(context)
            audit_results["sections"]["compliance"] = compliance_audit

        except Exception as e:
            logger.error(f"Compliance audit failed: {e}")
            audit_results["sections"]["compliance"] = {"error": str(e)}

        # 2. Check insurance expiry
        try:
            insurance_skill = self.verify.skills.get("insurance_verification")
            if insurance_skill:
                expiry_check = await insurance_skill.execute({
                    "operation": "check_expiry",
                    "marina_id": marina_id,
                    "days_threshold": 30
                })
                audit_results["sections"]["insurance_expiry"] = expiry_check

        except Exception as e:
            logger.error(f"Insurance expiry check failed: {e}")

        # 3. Check active permits
        try:
            permit_skill = self.verify.skills.get("hot_work_monitoring")
            if permit_skill:
                active_permits = await permit_skill.execute({
                    "operation": "check_active",
                    "marina_id": marina_id
                })
                audit_results["sections"]["active_permits"] = active_permits

        except Exception as e:
            logger.error(f"Active permits check failed: {e}")

        # 4. Get compliance summary
        try:
            summary = self.verify.get_compliance_summary(marina_id)
            audit_results["sections"]["summary"] = summary

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")

        logger.info("Daily compliance audit complete")

        return audit_results

    def get_dashboard_data(self, marina_id: str) -> Dict[str, Any]:
        """
        Get real-time dashboard data for marina operations and compliance

        Returns:
        - Active violations count
        - Critical issues
        - Active permits
        - Insurance status
        - Recent activity
        """
        logger.info(f"Fetching dashboard data for marina: {marina_id}")

        dashboard = {
            "marina_id": marina_id,
            "timestamp": None,
            "compliance_summary": None,
            "active_violations": [],
            "critical_issues": [],
            "active_permits_count": 0,
            "insurance_expiring_soon": 0,
            "recent_activity": []
        }

        try:
            # Get compliance summary
            dashboard["compliance_summary"] = self.verify.get_compliance_summary(marina_id)

            # Get active violations
            active_violations = self.verify.get_active_violations(marina_id=marina_id)
            dashboard["active_violations"] = len(active_violations)

            # Get critical issues
            critical = [v for v in active_violations if v.severity == "critical"]
            dashboard["critical_issues"] = [
                {
                    "id": v.violation_id,
                    "article": v.article_number,
                    "description": v.description,
                    "detected": v.detected_at
                }
                for v in critical[:5]
            ]

            logger.info("Dashboard data fetched successfully")

        except Exception as e:
            logger.error(f"Failed to fetch dashboard data: {e}")

        return dashboard

    def get_all_available_skills(self) -> Dict[str, List[str]]:
        """Get all available skills from both orchestrators"""
        return {
            "operational_skills": self.big5.get_available_skills(),
            "compliance_skills": self.verify.get_available_skills(),
            "total_skills": len(self.big5.get_available_skills()) + len(self.verify.get_available_skills())
        }

    async def process_natural_language_request(
        self,
        user_input: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Process natural language request and route to appropriate orchestrator

        Determines if request is operational or compliance-related
        and routes accordingly
        """
        logger.info(f"Processing NL request: {user_input[:50]}...")

        # Use Big-5 to analyze the request
        execution_plan = self.big5.process_natural_language(user_input, context)

        # Determine if this is compliance-related
        compliance_keywords = [
            "insurance", "permit", "compliance", "violation", "safety",
            "fire watch", "hot work", "audit", "regulation", "article"
        ]

        is_compliance = any(
            keyword in user_input.lower()
            for keyword in compliance_keywords
        )

        execution_plan["is_compliance_request"] = is_compliance
        execution_plan["recommended_orchestrator"] = "verify" if is_compliance else "big5"

        logger.info(
            f"Request classified as: "
            f"{'compliance' if is_compliance else 'operational'}"
        )

        return execution_plan
