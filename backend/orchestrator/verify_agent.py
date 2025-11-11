"""
VERIFY Agent - Security Management and Compliance Verification System

Handles:
- 176-article compliance checking
- Violation detection and logging
- Insurance verification (Article E.2.1)
- Hot work permit monitoring (Article E.5.5)
- Security incident management
- Real-time compliance monitoring
"""

import json
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

from anthropic import Anthropic

from ..config import get_config
from ..logger import setup_logger
from ..exceptions import OrchestratorError, SkillExecutionError
from ..database.models import (
    Insurance, Permit, Violation, ComplianceRule,
    SecurityIncident, Document,
    ViolationSeverity, ViolationStatus, ViolationType,
    InsuranceStatus, PermitStatus, PermitType
)


logger = setup_logger(__name__)


@dataclass
class ComplianceCheckResult:
    """Result from a compliance check"""
    rule_id: str
    article_number: str
    passed: bool
    severity: str
    violations_detected: List[str]
    timestamp: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class VerificationResult:
    """Result from VERIFY Agent execution"""
    check_type: str
    success: bool
    data: Any
    violations: List[Violation]
    execution_time: float
    timestamp: str
    error: Optional[str] = None


@dataclass
class VerifyContext:
    """Context for VERIFY Agent execution"""
    marina_id: str
    user_id: str
    session_id: str
    check_scope: str = "all"  # "all", "insurance", "permits", "safety", "environmental"
    auto_enforce: bool = False  # Automatically enforce violations
    metadata: Optional[Dict] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class VerifyAgent:
    """
    VERIFY Agent - Security Management and Compliance Verification

    Responsibilities:
    1. Monitor compliance with 176-article regulations
    2. Verify insurance coverage (Article E.2.1)
    3. Monitor hot work permits (Article E.5.5)
    4. Detect and log violations
    5. Manage security incidents
    6. Generate compliance reports
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the VERIFY Agent"""
        config = get_config()

        self.api_key = api_key or config.api.anthropic_api_key
        if not self.api_key:
            raise OrchestratorError("ANTHROPIC_API_KEY is required")

        try:
            self.client = Anthropic(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise OrchestratorError(f"Client initialization failed: {e}")

        # Load compliance rules
        self.compliance_rules = self._load_compliance_rules()

        # Initialize skill handlers
        self.skills: Dict[str, Any] = {}
        self.violation_log: List[Violation] = []
        self.check_history: List[ComplianceCheckResult] = []

        # In-memory storage (would be database in production)
        self.insurances: Dict[str, Insurance] = {}
        self.permits: Dict[str, Permit] = {}
        self.violations: Dict[str, Violation] = {}
        self.incidents: Dict[str, SecurityIncident] = {}

        logger.info("VERIFY Agent initialized with {} compliance rules".format(
            len(self.compliance_rules)
        ))

    def _load_compliance_rules(self) -> List[ComplianceRule]:
        """Load compliance rules from configuration"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "compliance_rules.json"

            if not config_path.exists():
                logger.warning(f"Compliance rules file not found: {config_path}")
                return []

            with open(config_path, 'r') as f:
                config = json.load(f)

            rules = []
            for rule_data in config.get('rules', []):
                rule = ComplianceRule(
                    rule_id=rule_data['rule_id'],
                    article_number=rule_data['article_number'],
                    title=rule_data['title'],
                    description=rule_data['description'],
                    category=rule_data['category'],
                    severity=rule_data['severity'],
                    conditions=rule_data.get('conditions', {}),
                    auto_check=rule_data.get('auto_check', True),
                    check_frequency_hours=rule_data.get('check_frequency_hours', 24),
                    notification_emails=rule_data.get('notification_emails', []),
                    escalation_threshold_hours=rule_data.get('escalation_threshold_hours', 24),
                    is_active=rule_data.get('is_active', True),
                    applies_to=rule_data.get('applies_to', [])
                )
                rules.append(rule)

            logger.info(f"Loaded {len(rules)} compliance rules")
            return rules

        except Exception as e:
            logger.error(f"Failed to load compliance rules: {e}")
            return []

    def register_skill(self, skill_name: str, skill_handler: Any) -> None:
        """Register a compliance skill handler"""
        if not hasattr(skill_handler, 'execute'):
            raise OrchestratorError(
                f"Skill {skill_name} must have 'execute' method"
            )

        self.skills[skill_name] = skill_handler
        logger.info(f"Registered VERIFY skill: {skill_name}")

    def get_available_skills(self) -> List[str]:
        """Get list of registered compliance skills"""
        return list(self.skills.keys())

    def get_rule_by_article(self, article_number: str) -> Optional[ComplianceRule]:
        """Get compliance rule by article number"""
        for rule in self.compliance_rules:
            if rule.article_number == article_number:
                return rule
        return None

    def get_rules_by_category(self, category: str) -> List[ComplianceRule]:
        """Get all compliance rules in a category"""
        return [rule for rule in self.compliance_rules if rule.category == category]

    async def verify_insurance(
        self,
        vessel_name: str,
        vessel_registration: str,
        marina_id: str,
        booking_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify insurance compliance per Article E.2.1

        Article E.2.1: Yacht must be covered under applicable Third-Party
        Financial Liability insurance in amount determined by Company.
        """
        logger.info(f"Verifying insurance for vessel: {vessel_name}")

        # Check if we have insurance skill registered
        if "insurance_verification" not in self.skills:
            logger.error("Insurance verification skill not registered")
            return {
                "success": False,
                "error": "Insurance verification skill not available"
            }

        # Execute insurance verification skill
        skill = self.skills["insurance_verification"]
        result = await skill.execute({
            "vessel_name": vessel_name,
            "vessel_registration": vessel_registration,
            "marina_id": marina_id,
            "booking_id": booking_id
        })

        # Check if insurance is valid
        if not result.get("insurance_valid", False):
            # Log violation
            violation = self._create_violation(
                rule_id="E.2.1",
                article_number="E.2.1",
                marina_id=marina_id,
                violation_type="insurance",
                severity="critical",
                description=f"Invalid or missing insurance for vessel {vessel_name}",
                entity_type="vessel",
                entity_id=vessel_registration,
                vessel_name=vessel_name,
                booking_id=booking_id
            )

            self.violations[violation.violation_id] = violation
            logger.warning(f"Insurance violation detected for {vessel_name}: {violation.violation_id}")

        return result

    async def monitor_hot_work_permit(
        self,
        permit_id: str,
        marina_id: str
    ) -> Dict[str, Any]:
        """
        Monitor hot work permit compliance per Article E.5.5

        Article E.5.5: During hot works (welding, grinding, sanding, etc.)
        all necessary measures must be taken to prevent pollution and damage.
        Works without proper measures will be interrupted immediately.
        """
        logger.info(f"Monitoring hot work permit: {permit_id}")

        # Check if permit exists
        if permit_id not in self.permits:
            return {
                "success": False,
                "error": f"Permit {permit_id} not found"
            }

        permit = self.permits[permit_id]

        # Check if hot work permit monitoring skill is registered
        if "hot_work_monitoring" not in self.skills:
            logger.error("Hot work monitoring skill not registered")
            return {
                "success": False,
                "error": "Hot work monitoring skill not available"
            }

        # Execute monitoring skill
        skill = self.skills["hot_work_monitoring"]
        result = await skill.execute({
            "permit_id": permit_id,
            "permit": permit,
            "marina_id": marina_id
        })

        # Check for violations
        if result.get("violations", []):
            for violation_desc in result["violations"]:
                violation = self._create_violation(
                    rule_id="E.5.5",
                    article_number="E.5.5",
                    marina_id=marina_id,
                    violation_type="safety",
                    severity="high",
                    description=violation_desc,
                    entity_type="vessel",
                    entity_id=permit.vessel_registration or "unknown",
                    vessel_name=permit.vessel_name,
                    permit_id=permit_id
                )

                self.violations[violation.violation_id] = violation
                logger.warning(f"Hot work violation detected: {violation.violation_id}")

        return result

    def check_compliance(
        self,
        rule_id: str,
        entity_type: str,
        entity_id: str,
        entity_data: Dict[str, Any],
        context: VerifyContext
    ) -> ComplianceCheckResult:
        """
        Check compliance against a specific rule
        """
        rule = self.get_rule_by_article(rule_id)
        if not rule:
            return ComplianceCheckResult(
                rule_id=rule_id,
                article_number=rule_id,
                passed=False,
                severity="medium",
                violations_detected=[f"Rule {rule_id} not found"],
                timestamp=datetime.now().isoformat()
            )

        violations_detected = []
        passed = True

        # Evaluate rule conditions
        conditions = rule.conditions

        # Example condition checks (would be more sophisticated in production)
        if rule.article_number == "E.2.1":
            # Insurance check
            if not entity_data.get("insurance_valid", False):
                violations_detected.append("Missing or invalid insurance")
                passed = False

        elif rule.article_number == "E.5.5":
            # Hot work check
            if not entity_data.get("permit_approved", False):
                violations_detected.append("Hot work without approved permit")
                passed = False
            if not entity_data.get("fire_watch_assigned", False):
                violations_detected.append("No fire watch assigned for hot work")
                passed = False

        # Create result
        result = ComplianceCheckResult(
            rule_id=rule.rule_id,
            article_number=rule.article_number,
            passed=passed,
            severity=rule.severity,
            violations_detected=violations_detected,
            timestamp=datetime.now().isoformat(),
            details={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "rule_title": rule.title
            }
        )

        self.check_history.append(result)

        # Log violations if any
        if not passed:
            for violation_desc in violations_detected:
                violation = self._create_violation(
                    rule_id=rule.rule_id,
                    article_number=rule.article_number,
                    marina_id=context.marina_id,
                    violation_type=self._map_category_to_violation_type(rule.category),
                    severity=rule.severity,
                    description=violation_desc,
                    entity_type=entity_type,
                    entity_id=entity_id
                )
                self.violations[violation.violation_id] = violation

        return result

    def run_compliance_audit(
        self,
        context: VerifyContext,
        scope: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive compliance audit

        Args:
            context: Verification context
            scope: List of article numbers to check (None = check all)

        Returns:
            Audit results with violations and recommendations
        """
        logger.info(f"Running compliance audit for marina: {context.marina_id}")

        rules_to_check = self.compliance_rules
        if scope:
            rules_to_check = [r for r in self.compliance_rules if r.article_number in scope]

        audit_results = {
            "marina_id": context.marina_id,
            "audit_timestamp": datetime.now().isoformat(),
            "total_rules_checked": len(rules_to_check),
            "rules_passed": 0,
            "rules_failed": 0,
            "violations_detected": [],
            "critical_issues": [],
            "recommendations": []
        }

        for rule in rules_to_check:
            if not rule.is_active or not rule.auto_check:
                continue

            # This is a simplified check - in production would check actual data
            logger.info(f"Checking rule: {rule.article_number} - {rule.title}")
            audit_results["rules_passed"] += 1

        # Get current violations
        audit_results["violations_detected"] = [
            asdict(v) for v in self.violations.values()
            if v.status != "resolved"
        ]

        audit_results["rules_failed"] = len(audit_results["violations_detected"])

        # Identify critical issues
        audit_results["critical_issues"] = [
            v for v in audit_results["violations_detected"]
            if v["severity"] == "critical"
        ]

        logger.info(
            f"Audit complete: {audit_results['rules_passed']} passed, "
            f"{audit_results['rules_failed']} failed"
        )

        return audit_results

    def get_active_violations(
        self,
        marina_id: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Violation]:
        """Get all active (unresolved) violations"""
        violations = [
            v for v in self.violations.values()
            if v.status != "resolved"
        ]

        if marina_id:
            violations = [v for v in violations if v.marina_id == marina_id]

        if severity:
            violations = [v for v in violations if v.severity == severity]

        return violations

    def resolve_violation(
        self,
        violation_id: str,
        resolved_by: str,
        resolution_notes: str
    ) -> bool:
        """Mark a violation as resolved"""
        if violation_id not in self.violations:
            logger.error(f"Violation {violation_id} not found")
            return False

        violation = self.violations[violation_id]
        violation.status = "resolved"
        violation.resolved_at = datetime.now().isoformat()
        violation.resolved_by = resolved_by
        violation.resolution_notes = resolution_notes

        logger.info(f"Violation {violation_id} resolved by {resolved_by}")
        return True

    def _create_violation(
        self,
        rule_id: str,
        article_number: str,
        marina_id: str,
        violation_type: str,
        severity: str,
        description: str,
        entity_type: str,
        entity_id: str,
        **kwargs
    ) -> Violation:
        """Create a new violation record"""
        violation = Violation(
            violation_id=str(uuid.uuid4()),
            rule_id=rule_id,
            article_number=article_number,
            marina_id=marina_id,
            violation_type=violation_type,
            severity=severity,
            detected_at=datetime.now().isoformat(),
            description=description,
            status="detected",
            entity_type=entity_type,
            entity_id=entity_id,
            **kwargs
        )

        return violation

    def _map_category_to_violation_type(self, category: str) -> str:
        """Map compliance category to violation type"""
        mapping = {
            "safety": "safety",
            "environmental": "environmental",
            "operational": "operational",
            "administrative": "administrative",
            "security": "security",
            "insurance_and_liability": "insurance",
            "permits_and_licenses": "permit"
        }
        return mapping.get(category, "operational")

    def get_compliance_summary(self, marina_id: str) -> Dict[str, Any]:
        """Get compliance summary for a marina"""
        violations = self.get_active_violations(marina_id=marina_id)

        return {
            "marina_id": marina_id,
            "timestamp": datetime.now().isoformat(),
            "total_active_violations": len(violations),
            "by_severity": {
                "critical": len([v for v in violations if v.severity == "critical"]),
                "high": len([v for v in violations if v.severity == "high"]),
                "medium": len([v for v in violations if v.severity == "medium"]),
                "low": len([v for v in violations if v.severity == "low"])
            },
            "by_type": {
                "safety": len([v for v in violations if v.violation_type == "safety"]),
                "environmental": len([v for v in violations if v.violation_type == "environmental"]),
                "insurance": len([v for v in violations if v.violation_type == "insurance"]),
                "permit": len([v for v in violations if v.violation_type == "permit"]),
                "security": len([v for v in violations if v.violation_type == "security"]),
                "operational": len([v for v in violations if v.violation_type == "operational"]),
                "administrative": len([v for v in violations if v.violation_type == "administrative"])
            },
            "recent_violations": [
                {
                    "id": v.violation_id,
                    "article": v.article_number,
                    "severity": v.severity,
                    "type": v.violation_type,
                    "description": v.description,
                    "detected_at": v.detected_at
                }
                for v in sorted(violations, key=lambda x: x.detected_at, reverse=True)[:10]
            ]
        }
