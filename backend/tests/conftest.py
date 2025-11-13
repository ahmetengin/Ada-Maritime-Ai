"""
Pytest Configuration and Fixtures
Common test fixtures for Ada Maritime AI test suite
"""

import pytest
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Set test environment
os.environ["ENV"] = "test"
os.environ["ANTHROPIC_API_KEY"] = "test-key"


@pytest.fixture
def sample_vessel_data() -> Dict[str, Any]:
    """Sample vessel data for testing"""
    return {
        "vessel_name": "Test Vessel",
        "vessel_registration": "TEST-001",
        "vessel_owner": "Test Owner",
        "vessel_type": "sailing_yacht",
        "length_meters": 15.5,
        "beam_meters": 4.2,
        "draft_meters": 2.1
    }


@pytest.fixture
def sample_insurance_data() -> Dict[str, Any]:
    """Sample insurance data for testing"""
    return {
        "insurance_id": "ins_test_001",
        "vessel_name": "Test Vessel",
        "vessel_registration": "TEST-001",
        "policy_number": "POL-123456",
        "insurance_type": "third_party_liability",
        "provider": "Test Insurance Co.",
        "coverage_amount": 1000000.0,
        "expiry_date": (datetime.now() + timedelta(days=180)).isoformat(),
        "status": "valid"
    }


@pytest.fixture
def sample_expired_insurance_data() -> Dict[str, Any]:
    """Sample expired insurance data for testing"""
    return {
        "insurance_id": "ins_test_002",
        "vessel_name": "Expired Vessel",
        "vessel_registration": "TEST-002",
        "policy_number": "POL-999999",
        "insurance_type": "third_party_liability",
        "provider": "Test Insurance Co.",
        "coverage_amount": 500000.0,
        "expiry_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "status": "expired"
    }


@pytest.fixture
def sample_permit_data() -> Dict[str, Any]:
    """Sample hot work permit data for testing"""
    return {
        "permit_id": "permit_test_001",
        "permit_type": "hot_work",
        "work_description": "Welding repairs on hull",
        "work_location": "Berth A12",
        "scheduled_start": (datetime.now() + timedelta(hours=2)).isoformat(),
        "scheduled_end": (datetime.now() + timedelta(hours=6)).isoformat(),
        "requested_by": "Test Requester",
        "requester_email": "test@example.com",
        "requester_phone": "+90 555 1234567",
        "marina_id": "marina_test",
        "status": "pending",
        "fire_watch_required": True,
        "safety_equipment_required": [
            "fire_extinguisher",
            "fire_blanket",
            "safety_goggles"
        ]
    }


@pytest.fixture
def sample_violation_data() -> Dict[str, Any]:
    """Sample violation data for testing"""
    return {
        "violation_id": "viol_test_001",
        "article_number": "E.2.1",
        "article_title": "Third-Party Financial Liability Insurance Requirement",
        "category": "insurance_and_liability",
        "severity": "critical",
        "description": "Vessel insurance expired",
        "entity_type": "vessel",
        "entity_id": "TEST-002",
        "detected_at": datetime.now().isoformat(),
        "status": "active",
        "required_actions": [
            "Renew insurance policy immediately",
            "Submit proof of insurance to marina office"
        ],
        "response_time_hours": 24
    }


@pytest.fixture
def sample_marina_config() -> Dict[str, Any]:
    """Sample marina configuration for testing"""
    return {
        "marina_id": "marina_test",
        "marina_name": "Test Marina",
        "location": "Test Location",
        "contact_email": "marina@test.com",
        "contact_phone": "+90 555 9999999",
        "total_berths": 100,
        "vhf_channel": 73,
        "emergency_channel": 16
    }


@pytest.fixture
def sample_vhf_communication() -> Dict[str, Any]:
    """Sample VHF communication data for testing"""
    return {
        "comm_id": "comm_test_001",
        "channel_number": 73,
        "frequency_mhz": 156.675,
        "communication_type": "intership",
        "vessel1_name": "Test Vessel 1",
        "vessel2_name": "Test Vessel 2",
        "timestamp": datetime.now().isoformat(),
        "transcription": "Test vessel calling, position update",
        "signal_strength": -65.5,
        "duration_seconds": 15.2
    }


@pytest.fixture
def mock_anthropic_api(monkeypatch):
    """Mock Anthropic API for testing"""
    class MockAnthropicClient:
        def __init__(self, api_key=None):
            self.api_key = api_key

        class messages:
            @staticmethod
            def create(*args, **kwargs):
                class MockMessage:
                    class content:
                        text = "Mock AI response"
                return MockMessage()

    monkeypatch.setattr("anthropic.Anthropic", MockAnthropicClient)
    return MockAnthropicClient


@pytest.fixture
def test_database():
    """Setup test database"""
    # Setup test database
    # You would initialize an in-memory SQLite database here
    # or use a test PostgreSQL database
    yield
    # Teardown
    pass


@pytest.fixture
def api_client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    # Import your FastAPI app
    # from backend.api import app
    # return TestClient(app)
    pass


# Async fixtures
@pytest.fixture
async def async_client():
    """Async test client for async endpoints"""
    from httpx import AsyncClient
    # async with AsyncClient(app=app, base_url="http://test") as client:
    #     yield client
    pass
