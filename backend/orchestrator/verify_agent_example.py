"""
VERIFY Agent Integration Example

Demonstrates how to use the VERIFY Agent with all compliance skills:
- Insurance Verification (Article E.2.1)
- Hot Work Permit Monitoring (Article E.5.5)
- Comprehensive Compliance Checking (176 articles)
- Violation Detection and Logging
"""

import asyncio
from datetime import datetime, timedelta

from verify_agent import VerifyAgent, VerifyContext
from ..skills.insurance_verification_skill import InsuranceVerificationSkill
from ..skills.hot_work_permit_skill import HotWorkPermitSkill
from ..skills.compliance_checking_skill import ComplianceCheckingSkill
from ..logger import setup_logger


logger = setup_logger(__name__)


async def example_insurance_verification():
    """Example: Insurance verification workflow"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Insurance Verification (Article E.2.1)")
    print("="*80 + "\n")

    # Initialize VERIFY Agent
    agent = VerifyAgent()

    # Register insurance verification skill
    insurance_skill = InsuranceVerificationSkill()
    agent.register_skill("insurance_verification", insurance_skill)

    # Example 1: Register new insurance
    print("Step 1: Register yacht insurance...")
    result = await insurance_skill.execute({
        "operation": "register",
        "vessel_name": "Sea Dream",
        "vessel_registration": "TR-123456",
        "policy_number": "INS-2024-001",
        "insurance_type": "comprehensive",
        "provider": "Allianz",
        "coverage_amount": 2000000,
        "currency": "EUR",
        "issue_date": datetime.now().isoformat(),
        "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
        "marina_id": "marina_001",
        "booking_id": "booking_001",
        "document_url": "https://example.com/insurance_docs/INS-2024-001.pdf"
    })

    print(f"Registration Result: {result['message']}")
    print(f"Insurance ID: {result['insurance_id']}")
    print(f"Status: {result['status']}")
    print(f"Auto-verified: {result['auto_verified']}\n")

    # Example 2: Verify insurance
    print("Step 2: Verify insurance compliance...")
    verify_result = await agent.verify_insurance(
        vessel_name="Sea Dream",
        vessel_registration="TR-123456",
        marina_id="marina_001",
        booking_id="booking_001"
    )

    print(f"Insurance Valid: {verify_result['insurance_valid']}")
    print(f"Marina Entry Permitted: {verify_result['marina_entry_permitted']}")

    if verify_result.get('violations'):
        print(f"Violations: {verify_result['violations']}")
    else:
        print("No violations detected")

    print(f"\nCompliance Checks:")
    for check, passed in verify_result['compliance_checks'].items():
        print(f"  - {check}: {'✓' if passed else '✗'}")


async def example_hot_work_permit():
    """Example: Hot work permit workflow"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Hot Work Permit Monitoring (Article E.5.5)")
    print("="*80 + "\n")

    # Initialize skills
    agent = VerifyAgent()
    hot_work_skill = HotWorkPermitSkill()
    agent.register_skill("hot_work_monitoring", hot_work_skill)

    # Example 1: Request hot work permit
    print("Step 1: Request hot work permit for welding...")
    request_result = await hot_work_skill.execute({
        "operation": "request",
        "marina_id": "marina_001",
        "berth_id": "berth_A12",
        "vessel_name": "Sea Dream",
        "vessel_registration": "TR-123456",
        "work_description": "Welding repairs on hull near waterline",
        "work_location": "Berth A12, starboard side",
        "scheduled_start": (datetime.now() + timedelta(hours=2)).isoformat(),
        "scheduled_end": (datetime.now() + timedelta(hours=6)).isoformat(),
        "requested_by": "Captain John Smith",
        "requester_email": "john.smith@seadream.com",
        "requester_phone": "+90 555 123 4567",
        "safety_zone_meters": 5.0
    })

    print(f"Permit ID: {request_result['permit_id']}")
    print(f"Permit Type: {request_result['permit_type']}")
    print(f"Fire Watch Required: {request_result['fire_watch_required']}")
    print(f"\nRequired Safety Equipment:")
    for equipment in request_result['safety_equipment_required']:
        print(f"  - {equipment}")
    print(f"\nSafety Conditions:")
    for condition in request_result['conditions']:
        print(f"  - {condition}")

    permit_id = request_result['permit_id']

    # Example 2: Approve permit
    print("\nStep 2: Approve hot work permit...")
    approve_result = await hot_work_skill.execute({
        "operation": "approve",
        "permit_id": permit_id,
        "approved_by": "Marina Manager - Sarah Johnson"
    })

    print(f"Status: {approve_result['status']}")
    print(f"Approved by: {approve_result['approved_by']}")
    print(f"Work can begin: {approve_result['work_can_begin']}")

    # Example 3: Monitor permit
    print("\nStep 3: Monitor hot work permit compliance...")
    monitor_result = await hot_work_skill.execute({
        "operation": "monitor",
        "permit_id": permit_id
    })

    print(f"Is Compliant: {monitor_result['is_compliant']}")
    print(f"Is Active: {monitor_result['is_active']}")

    if monitor_result['violations']:
        print(f"\nViolations Detected:")
        for violation in monitor_result['violations']:
            print(f"  ⚠ {violation}")

    if monitor_result['warnings']:
        print(f"\nWarnings:")
        for warning in monitor_result['warnings']:
            print(f"  ⚡ {warning}")


async def example_comprehensive_audit():
    """Example: Comprehensive compliance audit"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Comprehensive Compliance Audit (176 Articles)")
    print("="*80 + "\n")

    # Initialize agent and skills
    agent = VerifyAgent()
    compliance_skill = ComplianceCheckingSkill()

    # Example 1: Get all rules
    print("Step 1: Load compliance rules...")
    rules_result = await compliance_skill.execute({
        "operation": "get_rules"
    })

    print(f"Total Rules: {rules_result['total_rules']}")

    # Example 2: Check specific category
    print("\nStep 2: Check safety compliance...")
    safety_check = await compliance_skill.execute({
        "operation": "check_category",
        "category": "safety",
        "marina_id": "marina_001"
    })

    print(f"Safety Rules Checked: {safety_check['total_rules']}")
    print(f"Violations: {safety_check['violations_count']}")
    print(f"Compliance Rate: {safety_check['compliance_rate']}%")

    # Example 3: Comprehensive audit
    print("\nStep 3: Run comprehensive audit...")
    audit_result = await compliance_skill.execute({
        "operation": "audit",
        "marina_id": "marina_001",
        "include_recommendations": True
    })

    print(f"\nAudit Summary:")
    summary = audit_result['summary']
    print(f"  Total Rules Checked: {summary['total_rules_checked']}")
    print(f"  Total Violations: {summary['total_violations']}")
    print(f"  Critical Issues: {summary['critical_issues_count']}")
    print(f"  Compliance Rate: {summary['compliance_rate']}%")
    print(f"  Overall Status: {summary['overall_status']}")

    if audit_result['critical_issues']:
        print(f"\nCritical Issues:")
        for issue in audit_result['critical_issues']:
            print(f"  🔴 Article {issue['article']}: {issue['title']}")
            for violation in issue['violations']:
                print(f"     - {violation}")

    if audit_result['recommendations']:
        print(f"\nRecommendations:")
        for rec in audit_result['recommendations']:
            print(f"  💡 {rec}")


async def example_violation_management():
    """Example: Violation detection and management"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Violation Detection and Management")
    print("="*80 + "\n")

    agent = VerifyAgent()

    # Simulate creating a violation
    print("Step 1: Detect compliance violation...")

    context = VerifyContext(
        marina_id="marina_001",
        user_id="user_123",
        session_id="session_456",
        check_scope="insurance"
    )

    # Check compliance and detect violations
    check_result = agent.check_compliance(
        rule_id="E.2.1",
        entity_type="vessel",
        entity_id="TR-999999",
        entity_data={"insurance_valid": False},
        context=context
    )

    print(f"Rule: {check_result.article_number}")
    print(f"Passed: {check_result.passed}")
    print(f"Severity: {check_result.severity}")

    if check_result.violations_detected:
        print(f"\nViolations Detected:")
        for violation in check_result.violations_detected:
            print(f"  ⚠ {violation}")

    # Get active violations
    print("\nStep 2: Get active violations...")
    active_violations = agent.get_active_violations(
        marina_id="marina_001",
        severity="critical"
    )

    print(f"Active Critical Violations: {len(active_violations)}")
    for v in active_violations[:3]:  # Show first 3
        print(f"\n  Violation ID: {v.violation_id}")
        print(f"  Article: {v.article_number}")
        print(f"  Type: {v.violation_type}")
        print(f"  Description: {v.description}")
        print(f"  Detected: {v.detected_at}")

    # Get compliance summary
    print("\nStep 3: Get compliance summary...")
    summary = agent.get_compliance_summary("marina_001")

    print(f"\nMarina Compliance Summary:")
    print(f"  Total Active Violations: {summary['total_active_violations']}")
    print(f"\n  By Severity:")
    for severity, count in summary['by_severity'].items():
        print(f"    {severity}: {count}")
    print(f"\n  By Type:")
    for vtype, count in summary['by_type'].items():
        if count > 0:
            print(f"    {vtype}: {count}")


async def example_full_workflow():
    """Example: Complete compliance workflow"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Complete Marina Compliance Workflow")
    print("="*80 + "\n")

    # Initialize VERIFY Agent with all skills
    agent = VerifyAgent()

    # Register all skills
    agent.register_skill("insurance_verification", InsuranceVerificationSkill())
    agent.register_skill("hot_work_monitoring", HotWorkPermitSkill())

    print("VERIFY Agent initialized with all compliance skills\n")
    print("Available Skills:")
    for skill_name in agent.get_available_skills():
        print(f"  ✓ {skill_name}")

    # Run comprehensive audit
    print("\n" + "-"*80)
    print("Running Full Compliance Audit...")
    print("-"*80 + "\n")

    context = VerifyContext(
        marina_id="marina_001",
        user_id="admin_001",
        session_id="audit_session_001",
        check_scope="all"
    )

    audit = agent.run_compliance_audit(context)

    print("Audit Results:")
    print(f"  Marina: {audit['marina_id']}")
    print(f"  Timestamp: {audit['audit_timestamp']}")
    print(f"  Total Rules Checked: {audit['total_rules_checked']}")
    print(f"  Rules Passed: {audit['rules_passed']}")
    print(f"  Rules Failed: {audit['rules_failed']}")
    print(f"  Critical Issues: {len(audit['critical_issues'])}")

    if audit['violations_detected']:
        print(f"\n  Recent Violations:")
        for v in audit['violations_detected'][:5]:
            print(f"    - {v['article_number']}: {v['description']}")

    print("\n" + "="*80)
    print("VERIFY Agent - Compliance System Ready")
    print("="*80)


async def main():
    """Run all examples"""
    try:
        await example_insurance_verification()
        await example_hot_work_permit()
        await example_comprehensive_audit()
        await example_violation_management()
        await example_full_workflow()

        print("\n" + "="*80)
        print("All examples completed successfully!")
        print("="*80 + "\n")

    except Exception as e:
        logger.error(f"Example execution failed: {e}", exc_info=True)
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
