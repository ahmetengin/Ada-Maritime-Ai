"""
Ada Maritime AI - Main Application Entry Point

Initializes and runs the complete marina management system including:
- Big-5 Operational Orchestrator
- VERIFY Security & Compliance Agent
- Unified Marina Orchestrator
"""

import asyncio
from typing import Optional

from .orchestrator.unified_orchestrator import UnifiedMarinaOrchestrator
from .orchestrator.big5_orchestrator import AgentContext
from .orchestrator.verify_agent import VerifyContext
from .config import get_config
from .logger import setup_logger


logger = setup_logger(__name__)


class AdaMaritimeAI:
    """
    Ada Maritime AI - Complete Marina Management System

    Integrates operational and compliance/security capabilities
    for comprehensive marina operations.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Ada Maritime AI system"""
        logger.info("="*80)
        logger.info("Ada Maritime AI - Initialization Starting")
        logger.info("="*80)

        config = get_config()
        self.api_key = api_key or config.api.anthropic_api_key

        # Initialize Unified Orchestrator
        logger.info("Initializing Unified Marina Orchestrator...")
        self.orchestrator = UnifiedMarinaOrchestrator(api_key=self.api_key)

        # Get available skills
        skills = self.orchestrator.get_all_available_skills()

        logger.info("="*80)
        logger.info(f"Ada Maritime AI - Initialization Complete")
        logger.info(f"Total Skills Available: {skills['total_skills']}")
        logger.info(f"  - Operational Skills: {len(skills['operational_skills'])}")
        logger.info(f"  - Compliance Skills: {len(skills['compliance_skills'])}")
        logger.info("="*80)

    async def verify_vessel_entry(
        self,
        vessel_name: str,
        vessel_registration: str,
        marina_id: str,
        booking_id: Optional[str] = None
    ) -> dict:
        """
        Verify vessel compliance for marina entry

        Performs comprehensive compliance check per Article E.2.1 and other regulations
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"VESSEL ENTRY VERIFICATION")
        logger.info(f"Vessel: {vessel_name} ({vessel_registration})")
        logger.info(f"Marina: {marina_id}")
        logger.info(f"{'='*60}\n")

        result = await self.orchestrator.verify_vessel_compliance(
            vessel_name=vessel_name,
            vessel_registration=vessel_registration,
            marina_id=marina_id,
            booking_id=booking_id
        )

        # Log result
        if result["entry_authorized"]:
            logger.info(f"✅ ENTRY AUTHORIZED - Vessel is compliant")
        else:
            logger.warning(f"❌ ENTRY DENIED - Compliance issues detected")
            logger.warning(f"Violations: {len(result['violations'])}")

        return result

    async def request_hot_work_permit(
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
    ) -> dict:
        """
        Request hot work permit (Article E.5.5)

        Handles welding, grinding, painting, and other hot work activities
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"HOT WORK PERMIT REQUEST")
        logger.info(f"Work: {work_description[:50]}...")
        logger.info(f"Location: {work_location}")
        logger.info(f"{'='*60}\n")

        result = await self.orchestrator.process_hot_work_request(
            work_description=work_description,
            work_location=work_location,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            requested_by=requested_by,
            requester_email=requester_email,
            requester_phone=requester_phone,
            marina_id=marina_id,
            **kwargs
        )

        logger.info(f"✅ Permit Created: {result.get('permit_id')}")
        logger.info(f"Status: {result.get('status')}")
        logger.info(f"Fire Watch Required: {result.get('fire_watch_required')}")

        return result

    async def run_compliance_audit(self, marina_id: str) -> dict:
        """
        Run comprehensive compliance audit

        Checks all 176 articles and generates detailed report
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"COMPLIANCE AUDIT")
        logger.info(f"Marina: {marina_id}")
        logger.info(f"{'='*60}\n")

        result = await self.orchestrator.run_daily_compliance_audit(marina_id)

        # Log summary
        if "sections" in result and "summary" in result["sections"]:
            summary = result["sections"]["summary"]
            logger.info(f"\nAudit Summary:")
            logger.info(f"  Total Active Violations: {summary.get('total_active_violations', 0)}")
            logger.info(f"  Critical Issues: {summary['by_severity'].get('critical', 0)}")
            logger.info(f"  High Priority: {summary['by_severity'].get('high', 0)}")

        return result

    def get_dashboard(self, marina_id: str) -> dict:
        """Get real-time dashboard data"""
        logger.info(f"Fetching dashboard for marina: {marina_id}")
        return self.orchestrator.get_dashboard_data(marina_id)

    async def process_request(self, user_input: str, user_id: str, marina_id: str) -> dict:
        """
        Process natural language request

        Routes to appropriate orchestrator (operational or compliance)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"PROCESSING REQUEST")
        logger.info(f"User: {user_id}")
        logger.info(f"Input: {user_input[:100]}...")
        logger.info(f"{'='*60}\n")

        context = AgentContext(
            user_id=user_id,
            session_id=f"session_{user_id}",
            marina_id=marina_id,
            language="en"
        )

        result = await self.orchestrator.process_natural_language_request(
            user_input, context
        )

        logger.info(f"Request Type: {result.get('recommended_orchestrator', 'unknown')}")
        logger.info(f"Intent: {result.get('intent', 'unknown')}")

        return result


async def demo_usage():
    """
    Demo of Ada Maritime AI capabilities
    """
    print("\n" + "="*80)
    print("ADA MARITIME AI - DEMONSTRATION")
    print("="*80 + "\n")

    # Initialize system
    ada = AdaMaritimeAI()

    # 1. Vessel Entry Verification
    print("\n--- Demo 1: Vessel Entry Verification ---\n")
    vessel_check = await ada.verify_vessel_entry(
        vessel_name="Sea Dream",
        vessel_registration="TR-123456",
        marina_id="marina_001"
    )
    print(f"Entry Authorized: {vessel_check['entry_authorized']}")
    if not vessel_check['entry_authorized']:
        print(f"Required Actions: {vessel_check['required_actions']}")

    # 2. Hot Work Permit Request
    print("\n--- Demo 2: Hot Work Permit Request ---\n")
    from datetime import datetime, timedelta

    permit = await ada.request_hot_work_permit(
        work_description="Welding repairs on hull near waterline",
        work_location="Berth A12, starboard side",
        scheduled_start=(datetime.now() + timedelta(hours=2)).isoformat(),
        scheduled_end=(datetime.now() + timedelta(hours=6)).isoformat(),
        requested_by="Captain John Smith",
        requester_email="john.smith@seadream.com",
        requester_phone="+90 555 123 4567",
        marina_id="marina_001",
        vessel_name="Sea Dream",
        berth_id="berth_A12"
    )
    print(f"Permit ID: {permit['permit_id']}")
    print(f"Status: {permit['status']}")
    print(f"Safety Equipment Required: {len(permit['safety_equipment_required'])} items")

    # 3. Compliance Audit
    print("\n--- Demo 3: Compliance Audit ---\n")
    audit = await ada.run_compliance_audit("marina_001")
    if "sections" in audit and "summary" in audit["sections"]:
        summary = audit["sections"]["summary"]
        print(f"Total Violations: {summary.get('total_active_violations', 0)}")
        print(f"Critical Issues: {summary['by_severity'].get('critical', 0)}")

    # 4. Dashboard
    print("\n--- Demo 4: Real-Time Dashboard ---\n")
    dashboard = ada.get_dashboard("marina_001")
    print(f"Active Violations: {dashboard['active_violations']}")
    print(f"Critical Issues: {len(dashboard['critical_issues'])}")

    # 5. Natural Language Processing
    print("\n--- Demo 5: Natural Language Request ---\n")
    nl_result = await ada.process_request(
        "Check insurance status for all vessels",
        user_id="admin_001",
        marina_id="marina_001"
    )
    print(f"Intent: {nl_result.get('intent')}")
    print(f"Recommended Orchestrator: {nl_result.get('recommended_orchestrator')}")

    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80 + "\n")


def main():
    """Main entry point"""
    try:
        # Run demo
        asyncio.run(demo_usage())

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
