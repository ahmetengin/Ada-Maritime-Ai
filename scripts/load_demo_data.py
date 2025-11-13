#!/usr/bin/env python3
"""
Load Demo Data for Ada Maritime AI
Creates sample vessels, insurance records, permits, and violations for demonstration
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from database.models import (
    Vessel, Insurance, Permit, Violation,
    VesselType, InsuranceStatus, PermitStatus, ViolationStatus, ViolationSeverity
)


def create_demo_vessels():
    """Create demo vessels with various compliance states"""

    vessels = [
        # Vessel with expired insurance (for violation demo)
        {
            "vessel_id": "vessel_demo_001",
            "vessel_name": "Sea Dream",
            "vessel_registration": "TR-123456",
            "vessel_type": VesselType.SAILING_YACHT,
            "vessel_owner": "John Smith",
            "length_meters": 18.5,
            "beam_meters": 5.2,
            "draft_meters": 2.8,
            "marina_id": "marina_demo_001"
        },
        # Vessel with valid insurance (for success demo)
        {
            "vessel_id": "vessel_demo_002",
            "vessel_name": "Ocean Star",
            "vessel_registration": "TR-789012",
            "vessel_type": VesselType.MOTOR_YACHT,
            "vessel_owner": "Captain Smith",
            "length_meters": 22.0,
            "beam_meters": 6.5,
            "draft_meters": 3.2,
            "marina_id": "marina_demo_001"
        },
        # Vessel with insurance expiring soon
        {
            "vessel_id": "vessel_demo_003",
            "vessel_name": "Marina Dream",
            "vessel_registration": "TR-345678",
            "vessel_type": VesselType.SAILING_YACHT,
            "vessel_owner": "Jane Doe",
            "length_meters": 15.0,
            "beam_meters": 4.5,
            "draft_meters": 2.0,
            "marina_id": "marina_demo_001"
        },
        # Additional demo vessels
        {
            "vessel_id": "vessel_demo_004",
            "vessel_name": "Blue Horizon",
            "vessel_registration": "TR-901234",
            "vessel_type": VesselType.CATAMARAN,
            "vessel_owner": "Bob Johnson",
            "length_meters": 12.5,
            "beam_meters": 6.8,
            "draft_meters": 1.2,
            "marina_id": "marina_demo_001"
        },
        {
            "vessel_id": "vessel_demo_005",
            "vessel_name": "Wind Dancer",
            "vessel_registration": "TR-567890",
            "vessel_type": VesselType.SAILING_YACHT,
            "vessel_owner": "Alice Williams",
            "length_meters": 16.8,
            "beam_meters": 4.8,
            "draft_meters": 2.5,
            "marina_id": "marina_demo_001"
        }
    ]

    print("\n📋 Creating demo vessels...")
    for vessel_data in vessels:
        print(f"  ✓ {vessel_data['vessel_name']} ({vessel_data['vessel_registration']})")

    return vessels


def create_demo_insurance():
    """Create demo insurance records"""

    now = datetime.now()

    insurance_records = [
        # Expired insurance for Sea Dream (violation scenario)
        {
            "insurance_id": "ins_demo_001",
            "vessel_name": "Sea Dream",
            "vessel_registration": "TR-123456",
            "policy_number": "POL-EXPIRED-001",
            "insurance_type": "third_party_liability",
            "provider": "Demo Insurance Co.",
            "coverage_amount": 800000.0,
            "coverage_currency": "EUR",
            "issue_date": (now - timedelta(days=380)).isoformat(),
            "expiry_date": (now - timedelta(days=15)).isoformat(),
            "status": InsuranceStatus.EXPIRED
        },
        # Valid insurance for Ocean Star
        {
            "insurance_id": "ins_demo_002",
            "vessel_name": "Ocean Star",
            "vessel_registration": "TR-789012",
            "policy_number": "POL-VALID-002",
            "insurance_type": "third_party_liability",
            "provider": "Turkish Marine Insurance",
            "coverage_amount": 1500000.0,
            "coverage_currency": "EUR",
            "issue_date": (now - timedelta(days=30)).isoformat(),
            "expiry_date": (now + timedelta(days=335)).isoformat(),
            "status": InsuranceStatus.VALID
        },
        # Insurance expiring soon for Marina Dream
        {
            "insurance_id": "ins_demo_003",
            "vessel_name": "Marina Dream",
            "vessel_registration": "TR-345678",
            "policy_number": "POL-EXPIRING-003",
            "insurance_type": "third_party_liability",
            "provider": "Aegean Insurance Ltd.",
            "coverage_amount": 1000000.0,
            "coverage_currency": "EUR",
            "issue_date": (now - timedelta(days=340)).isoformat(),
            "expiry_date": (now + timedelta(days=25)).isoformat(),
            "status": InsuranceStatus.VALID
        },
        # Valid insurance for Blue Horizon
        {
            "insurance_id": "ins_demo_004",
            "vessel_name": "Blue Horizon",
            "vessel_registration": "TR-901234",
            "policy_number": "POL-VALID-004",
            "insurance_type": "third_party_liability",
            "provider": "Mediterranean Marine Insurance",
            "coverage_amount": 700000.0,
            "coverage_currency": "EUR",
            "issue_date": (now - timedelta(days=60)).isoformat(),
            "expiry_date": (now + timedelta(days=305)).isoformat(),
            "status": InsuranceStatus.VALID
        },
        # Valid insurance for Wind Dancer
        {
            "insurance_id": "ins_demo_005",
            "vessel_name": "Wind Dancer",
            "vessel_registration": "TR-567890",
            "policy_number": "POL-VALID-005",
            "insurance_type": "third_party_liability",
            "provider": "Turkish Marine Insurance",
            "coverage_amount": 900000.0,
            "coverage_currency": "EUR",
            "issue_date": (now - timedelta(days=90)).isoformat(),
            "expiry_date": (now + timedelta(days=275)).isoformat(),
            "status": InsuranceStatus.VALID
        }
    ]

    print("\n🛡️  Creating demo insurance records...")
    for ins in insurance_records:
        status_icon = "❌" if ins["status"] == InsuranceStatus.EXPIRED else "✓"
        print(f"  {status_icon} {ins['vessel_name']}: {ins['policy_number']} ({ins['status']})")

    return insurance_records


def create_demo_violations():
    """Create demo violations"""

    now = datetime.now()

    violations = [
        # Critical: Expired insurance for Sea Dream
        {
            "violation_id": "viol_demo_001",
            "article_number": "E.2.1",
            "article_title": "Third-Party Financial Liability Insurance Requirement",
            "category": "insurance_and_liability",
            "severity": ViolationSeverity.CRITICAL,
            "description": "Vessel insurance expired 15 days ago",
            "entity_type": "vessel",
            "entity_id": "TR-123456",
            "detected_at": now.isoformat(),
            "status": ViolationStatus.ACTIVE,
            "required_actions": [
                "Renew third-party liability insurance immediately",
                "Submit proof of insurance to marina office",
                "Vessel entry denied until compliance"
            ],
            "marina_id": "marina_demo_001",
            "response_time_hours": 24
        },
        # Medium: Insurance expiring soon for Marina Dream
        {
            "violation_id": "viol_demo_002",
            "article_number": "E.2.1",
            "article_title": "Third-Party Financial Liability Insurance Requirement",
            "category": "insurance_and_liability",
            "severity": ViolationSeverity.MEDIUM,
            "description": "Insurance expiring in 25 days - renewal reminder",
            "entity_type": "vessel",
            "entity_id": "TR-345678",
            "detected_at": now.isoformat(),
            "status": ViolationStatus.ACTIVE,
            "required_actions": [
                "Contact insurance provider for renewal",
                "Update marina with new policy details"
            ],
            "marina_id": "marina_demo_001",
            "response_time_hours": 168  # 7 days
        }
    ]

    print("\n⚠️  Creating demo violations...")
    for viol in violations:
        severity_icon = {"critical": "🚨", "high": "⚠️", "medium": "⚡", "low": "ℹ️"}.get(viol["severity"], "⚠️")
        print(f"  {severity_icon} Article {viol['article_number']}: {viol['entity_id']} ({viol['severity'].upper()})")

    return violations


def create_demo_permits():
    """Create demo hot work permits"""

    now = datetime.now()

    permits = [
        # Pending approval
        {
            "permit_id": "permit_demo_001",
            "permit_type": "hot_work",
            "work_description": "Welding repairs on hull - underwater hull damage",
            "work_location": "Berth A12",
            "vessel_name": "Ocean Star",
            "vessel_registration": "TR-789012",
            "scheduled_start": (now + timedelta(hours=2)).isoformat(),
            "scheduled_end": (now + timedelta(hours=8)).isoformat(),
            "requested_by": "Captain Smith",
            "requester_email": "smith@oceanstar.com",
            "requester_phone": "+90 555 1234567",
            "requested_at": now.isoformat(),
            "marina_id": "marina_demo_001",
            "status": PermitStatus.PENDING,
            "fire_watch_required": True,
            "safety_equipment_required": [
                "fire_extinguisher",
                "fire_blanket",
                "safety_goggles",
                "protective_gloves",
                "welding_screen"
            ]
        },
        # Active permit
        {
            "permit_id": "permit_demo_002",
            "permit_type": "hot_work",
            "work_description": "Grinding and painting - deck maintenance",
            "work_location": "Berth B05",
            "vessel_name": "Blue Horizon",
            "vessel_registration": "TR-901234",
            "scheduled_start": (now - timedelta(hours=1)).isoformat(),
            "scheduled_end": (now + timedelta(hours=3)).isoformat(),
            "requested_by": "Bob Johnson",
            "requester_email": "bob@bluehorizon.com",
            "requester_phone": "+90 555 9876543",
            "requested_at": (now - timedelta(hours=25)).isoformat(),
            "approved_at": (now - timedelta(hours=2)).isoformat(),
            "approved_by": "marina_manager",
            "actual_start": (now - timedelta(hours=1)).isoformat(),
            "marina_id": "marina_demo_001",
            "status": PermitStatus.ACTIVE,
            "fire_watch_required": True,
            "fire_watch_present": True,
            "safety_equipment_required": [
                "fire_extinguisher",
                "safety_goggles",
                "dust_mask",
                "hearing_protection"
            ]
        },
        # Completed permit
        {
            "permit_id": "permit_demo_003",
            "permit_type": "hot_work",
            "work_description": "Engine repair - exhaust system welding",
            "work_location": "Berth C20",
            "vessel_name": "Wind Dancer",
            "vessel_registration": "TR-567890",
            "scheduled_start": (now - timedelta(days=1, hours=6)).isoformat(),
            "scheduled_end": (now - timedelta(days=1)).isoformat(),
            "requested_by": "Alice Williams",
            "requester_email": "alice@winddancer.com",
            "requester_phone": "+90 555 1112233",
            "requested_at": (now - timedelta(days=2)).isoformat(),
            "approved_at": (now - timedelta(days=1, hours=7)).isoformat(),
            "approved_by": "marina_manager",
            "actual_start": (now - timedelta(days=1, hours=6)).isoformat(),
            "actual_end": (now - timedelta(days=1, hours=1)).isoformat(),
            "marina_id": "marina_demo_001",
            "status": PermitStatus.COMPLETED,
            "fire_watch_required": True,
            "fire_watch_present": True,
            "safety_equipment_required": [
                "fire_extinguisher",
                "fire_blanket",
                "safety_goggles",
                "welding_helmet"
            ]
        }
    ]

    print("\n🔥 Creating demo hot work permits...")
    for permit in permits:
        status_icon = {"pending": "⏳", "approved": "✅", "active": "🔄", "completed": "✓"}.get(permit["status"], "📋")
        print(f"  {status_icon} {permit['work_location']}: {permit['work_description'][:40]}... ({permit['status'].upper()})")

    return permits


def create_demo_marina_config():
    """Create demo marina configuration"""

    marina = {
        "marina_id": "marina_demo_001",
        "marina_name": "Demo Marina",
        "location": "Istanbul, Turkey",
        "contact_email": "manager@demo-marina.com",
        "contact_phone": "+90 555 0001111",
        "total_berths": 100,
        "occupied_berths": 85,
        "vhf_channel": 73,
        "vhf_frequency": 156.675,
        "emergency_channel": 16,
        "intership_channels": [6, 72, 73]
    }

    print("\n⚓ Creating demo marina configuration...")
    print(f"  ✓ {marina['marina_name']} - {marina['location']}")
    print(f"    VHF: CH {marina['vhf_channel']} ({marina['vhf_frequency']} MHz)")
    print(f"    Berths: {marina['occupied_berths']}/{marina['total_berths']} occupied")

    return marina


def main():
    """Load all demo data"""

    print("=" * 60)
    print("🚢 Ada Maritime AI - Demo Data Loader")
    print("=" * 60)

    # Create demo data
    vessels = create_demo_vessels()
    insurance = create_demo_insurance()
    violations = create_demo_violations()
    permits = create_demo_permits()
    marina = create_demo_marina_config()

    # Summary
    print("\n" + "=" * 60)
    print("✅ Demo Data Summary")
    print("=" * 60)
    print(f"  Vessels:    {len(vessels)}")
    print(f"  Insurance:  {len(insurance)}")
    print(f"  Violations: {len(violations)}")
    print(f"  Permits:    {len(permits)}")
    print(f"  Marina:     {marina['marina_name']}")

    print("\n🎯 Demo Scenarios Ready:")
    print("  1. Vessel entry denied (Sea Dream - expired insurance)")
    print("  2. Vessel entry approved (Ocean Star - valid insurance)")
    print("  3. Hot work permit workflow (Ocean Star - pending approval)")
    print("  4. Active permit monitoring (Blue Horizon - work in progress)")
    print("  5. Insurance expiry warning (Marina Dream - 25 days)")

    print("\n📊 Access demo at:")
    print("  Dashboard: http://localhost:3000/dashboard")
    print("  API: http://localhost:8000/api/v1")

    print("\n" + "=" * 60)
    print("✓ Demo data loaded successfully!")
    print("=" * 60)

    # In production, this would actually write to database
    # For now, it's a preparation script that generates the structure

    return {
        "vessels": vessels,
        "insurance": insurance,
        "violations": violations,
        "permits": permits,
        "marina": marina
    }


if __name__ == "__main__":
    demo_data = main()
