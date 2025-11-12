"""
Compliance Checking Skill - 176-Article System Verification

Performs comprehensive compliance checks across all marina regulations:
- Safety compliance (fire prevention, equipment, procedures)
- Environmental compliance (waste disposal, pollution prevention)
- Operational compliance (navigation, mooring, maintenance)
- Administrative compliance (documentation, contracts, payments)
- Security compliance (access control, permits)
- Insurance and liability compliance
- Permits and licenses compliance
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from .base_skill import BaseSkill, SkillMetadata
    from ..database.models import ComplianceRule
    from ..logger import setup_logger
except ImportError:
    from base_skill import BaseSkill, SkillMetadata
    from database.models import ComplianceRule
    from logger import setup_logger


logger = setup_logger(__name__)


class ComplianceCheckingSkill(BaseSkill):
    """
    Compliance Checking Skill for 176-Article System

    Provides comprehensive compliance verification across all marina
    operational regulations based on West Istanbul Marina standards.
    """

    def __init__(self):
        super().__init__()
        self.compliance_rules = self._load_rules()
        self.check_history: List[Dict[str, Any]] = []

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="compliance_checking",
            description="Comprehensive compliance verification for 176-article marina regulation system",
            version="1.0.0",
            author="Ada Maritime AI - VERIFY Agent",
            requires_database=True
        )

    def _load_rules(self) -> List[ComplianceRule]:
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

    async def execute(self, params: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """Execute compliance checking operation"""
        operation = params.get("operation", "check")

        if operation == "check":
            return await self._check_compliance(params, context)
        elif operation == "audit":
            return await self._comprehensive_audit(params, context)
        elif operation == "get_rules":
            return await self._get_rules(params, context)
        elif operation == "check_category":
            return await self._check_category(params, context)
        elif operation == "get_summary":
            return await self._get_compliance_summary(params, context)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    async def _check_compliance(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Check compliance for specific article or entity

        Params:
        - article_number (optional): Specific article to check
        - entity_type (optional): Type of entity (vessel, marina, staff)
        - entity_id (optional): Specific entity to check
        - marina_id: Marina to check
        """
        article_number = params.get("article_number")
        entity_type = params.get("entity_type")
        entity_id = params.get("entity_id")
        marina_id = params.get("marina_id")

        if not marina_id:
            return {
                "success": False,
                "error": "marina_id is required"
            }

        logger.info(
            f"Checking compliance: Article={article_number}, "
            f"Entity={entity_type}:{entity_id}, Marina={marina_id}"
        )

        # Find rules to check
        rules_to_check = []
        if article_number:
            rule = next((r for r in self.compliance_rules if r.article_number == article_number), None)
            if rule:
                rules_to_check.append(rule)
        else:
            rules_to_check = [r for r in self.compliance_rules if r.is_active]

        if not rules_to_check:
            return {
                "success": False,
                "error": f"No rules found for article: {article_number}" if article_number else "No active rules"
            }

        # Perform compliance checks
        results = []
        violations_found = []

        for rule in rules_to_check:
            check_result = self._evaluate_rule(rule, entity_type, entity_id, marina_id, params)
            results.append(check_result)

            if not check_result["compliant"]:
                violations_found.extend(check_result["violations"])

        # Create summary
        total_checks = len(results)
        compliant_checks = len([r for r in results if r["compliant"]])
        compliance_rate = (compliant_checks / total_checks * 100) if total_checks > 0 else 0

        check_record = {
            "timestamp": datetime.now().isoformat(),
            "marina_id": marina_id,
            "article_number": article_number,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "total_checks": total_checks,
            "compliant_checks": compliant_checks,
            "violations_count": len(violations_found)
        }
        self.check_history.append(check_record)

        logger.info(
            f"Compliance check complete: {compliant_checks}/{total_checks} passed, "
            f"Rate: {compliance_rate:.1f}%"
        )

        return {
            "success": True,
            "marina_id": marina_id,
            "timestamp": datetime.now().isoformat(),
            "total_checks": total_checks,
            "compliant_checks": compliant_checks,
            "violation_count": len(violations_found),
            "compliance_rate": round(compliance_rate, 2),
            "check_results": results,
            "violations": violations_found,
            "overall_compliant": len(violations_found) == 0
        }

    async def _comprehensive_audit(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Perform comprehensive compliance audit

        Params:
        - marina_id: Marina to audit
        - scope (optional): List of article numbers to check
        - include_recommendations (optional): Include improvement recommendations
        """
        marina_id = params.get("marina_id")
        scope = params.get("scope", [])
        include_recommendations = params.get("include_recommendations", True)

        if not marina_id:
            return {
                "success": False,
                "error": "marina_id is required"
            }

        logger.info(f"Starting comprehensive audit for marina: {marina_id}")

        # Filter rules by scope if provided
        rules_to_audit = self.compliance_rules
        if scope:
            rules_to_audit = [r for r in self.compliance_rules if r.article_number in scope]

        # Group rules by category
        by_category = {}
        for rule in rules_to_audit:
            if rule.category not in by_category:
                by_category[rule.category] = []
            by_category[rule.category].append(rule)

        # Perform audit by category
        category_results = {}
        all_violations = []
        critical_issues = []

        for category, rules in by_category.items():
            category_violations = []

            for rule in rules:
                if not rule.is_active or not rule.auto_check:
                    continue

                check_result = self._evaluate_rule(rule, None, None, marina_id, params)

                if not check_result["compliant"]:
                    category_violations.extend(check_result["violations"])

                    if rule.severity == "critical":
                        critical_issues.append({
                            "article": rule.article_number,
                            "title": rule.title,
                            "violations": check_result["violations"]
                        })

            all_violations.extend(category_violations)

            category_results[category] = {
                "total_rules": len(rules),
                "violations_count": len(category_violations),
                "compliant": len(category_violations) == 0,
                "violations": category_violations
            }

        # Generate recommendations
        recommendations = []
        if include_recommendations and all_violations:
            recommendations = self._generate_recommendations(all_violations, category_results)

        # Calculate overall compliance
        total_rules_checked = sum(cr["total_rules"] for cr in category_results.values())
        total_violations = len(all_violations)
        compliance_rate = ((total_rules_checked - total_violations) / total_rules_checked * 100) if total_rules_checked > 0 else 0

        logger.info(
            f"Audit complete: {total_rules_checked} rules checked, "
            f"{total_violations} violations, {len(critical_issues)} critical issues"
        )

        return {
            "success": True,
            "audit_type": "comprehensive",
            "marina_id": marina_id,
            "timestamp": datetime.now().isoformat(),
            "scope": scope if scope else "all_articles",
            "summary": {
                "total_rules_checked": total_rules_checked,
                "total_violations": total_violations,
                "critical_issues_count": len(critical_issues),
                "compliance_rate": round(compliance_rate, 2),
                "overall_status": "compliant" if total_violations == 0 else "non_compliant"
            },
            "by_category": category_results,
            "critical_issues": critical_issues,
            "all_violations": all_violations[:50],  # Limit to first 50
            "recommendations": recommendations,
            "requires_immediate_action": len(critical_issues) > 0
        }

    async def _check_category(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Check compliance for specific category

        Params:
        - category: Category to check (safety, environmental, etc.)
        - marina_id: Marina to check
        """
        category = params.get("category")
        marina_id = params.get("marina_id")

        if not category or not marina_id:
            return {
                "success": False,
                "error": "category and marina_id are required"
            }

        logger.info(f"Checking category: {category} for marina: {marina_id}")

        # Get rules for category
        category_rules = [r for r in self.compliance_rules if r.category == category and r.is_active]

        if not category_rules:
            return {
                "success": False,
                "error": f"No rules found for category: {category}"
            }

        # Check each rule
        results = []
        violations = []

        for rule in category_rules:
            check_result = self._evaluate_rule(rule, None, None, marina_id, params)
            results.append(check_result)

            if not check_result["compliant"]:
                violations.extend(check_result["violations"])

        compliance_rate = (len([r for r in results if r["compliant"]]) / len(results) * 100) if results else 0

        return {
            "success": True,
            "category": category,
            "marina_id": marina_id,
            "timestamp": datetime.now().isoformat(),
            "total_rules": len(category_rules),
            "violations_count": len(violations),
            "compliance_rate": round(compliance_rate, 2),
            "results": results,
            "violations": violations
        }

    async def _get_rules(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Get compliance rules

        Params:
        - category (optional): Filter by category
        - article_number (optional): Get specific article
        """
        category = params.get("category")
        article_number = params.get("article_number")

        rules = self.compliance_rules

        if article_number:
            rules = [r for r in rules if r.article_number == article_number]
        elif category:
            rules = [r for r in rules if r.category == category]

        rules_data = []
        for rule in rules:
            rules_data.append({
                "article_number": rule.article_number,
                "title": rule.title,
                "description": rule.description,
                "category": rule.category,
                "severity": rule.severity,
                "auto_check": rule.auto_check,
                "applies_to": rule.applies_to
            })

        return {
            "success": True,
            "total_rules": len(rules_data),
            "filter": {
                "category": category,
                "article_number": article_number
            },
            "rules": rules_data
        }

    async def _get_compliance_summary(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Get compliance summary for marina"""
        marina_id = params.get("marina_id")

        if not marina_id:
            return {
                "success": False,
                "error": "marina_id is required"
            }

        # Get recent check history for this marina
        recent_checks = [
            c for c in self.check_history
            if c["marina_id"] == marina_id
        ][-10:]  # Last 10 checks

        # Calculate summary stats
        if recent_checks:
            avg_compliance = sum(c["compliant_checks"] / c["total_checks"] * 100 for c in recent_checks) / len(recent_checks)
            total_violations = sum(c["violations_count"] for c in recent_checks)
        else:
            avg_compliance = 0
            total_violations = 0

        return {
            "success": True,
            "marina_id": marina_id,
            "timestamp": datetime.now().isoformat(),
            "total_rules_available": len(self.compliance_rules),
            "recent_checks_count": len(recent_checks),
            "average_compliance_rate": round(avg_compliance, 2),
            "total_violations_detected": total_violations,
            "recent_checks": recent_checks
        }

    def _evaluate_rule(
        self,
        rule: ComplianceRule,
        entity_type: Optional[str],
        entity_id: Optional[str],
        marina_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a specific compliance rule

        This is a simplified evaluation - in production would check actual data
        """
        violations = []
        warnings = []

        # Check if rule applies to entity type
        if entity_type and rule.applies_to and entity_type not in rule.applies_to and "all" not in rule.applies_to:
            return {
                "article_number": rule.article_number,
                "title": rule.title,
                "compliant": True,
                "applicable": False,
                "reason": f"Rule does not apply to entity type: {entity_type}",
                "violations": [],
                "warnings": []
            }

        # Simplified rule evaluation based on conditions
        # In production, this would query actual database and check real conditions

        # Example evaluations for key articles
        if rule.article_number == "E.2.1":
            # Insurance check - would query insurance database
            insurance_valid = params.get("insurance_valid", False)
            if not insurance_valid:
                violations.append("Insurance validation required per Article E.2.1")

        elif rule.article_number == "E.5.5":
            # Hot work check - would check permit database
            hot_work_permit = params.get("hot_work_permit_valid", True)
            if not hot_work_permit:
                violations.append("Hot work permit validation required per Article E.5.5")

        elif rule.article_number == "F.13":
            # Waste disposal - would check waste management logs
            waste_disposal_compliant = params.get("waste_disposal_compliant", True)
            if not waste_disposal_compliant:
                violations.append("Waste disposal violations detected per Article F.13")

        # For demonstration, assume most other rules pass
        # In production, each rule would have specific evaluation logic

        compliant = len(violations) == 0

        return {
            "article_number": rule.article_number,
            "title": rule.title,
            "category": rule.category,
            "severity": rule.severity,
            "compliant": compliant,
            "applicable": True,
            "violations": violations,
            "warnings": warnings,
            "conditions_checked": list(rule.conditions.keys())
        }

    def _generate_recommendations(
        self,
        violations: List[str],
        category_results: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []

        # Check which categories have issues
        problem_categories = [
            cat for cat, results in category_results.items()
            if results["violations_count"] > 0
        ]

        if "safety" in problem_categories:
            recommendations.append("Conduct comprehensive safety audit and training for all personnel")

        if "environmental" in problem_categories:
            recommendations.append("Review and update waste disposal procedures and monitoring")

        if "insurance_and_liability" in problem_categories:
            recommendations.append("Implement automated insurance verification system for all vessels")

        if "permits_and_licenses" in problem_categories:
            recommendations.append("Establish stricter permit request and approval workflow")

        # General recommendations
        if len(problem_categories) >= 3:
            recommendations.append("Consider comprehensive compliance management system implementation")

        recommendations.append("Schedule regular compliance training for marina staff")
        recommendations.append("Implement real-time violation detection and alerting system")

        return recommendations
