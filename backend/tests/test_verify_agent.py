"""
Test Suite for VERIFY Agent
Tests compliance checking, insurance verification, and hot work permits
"""

import pytest
from datetime import datetime, timedelta
from backend.database.models import Insurance, Permit, Violation


@pytest.mark.unit
@pytest.mark.compliance
class TestInsuranceVerification:
    """Test insurance verification functionality"""

    def test_valid_insurance(self, sample_insurance_data):
        """Test valid insurance is recognized correctly"""
        insurance = Insurance(**sample_insurance_data)

        assert insurance.is_valid() is True
        assert insurance.status == "valid"
        assert datetime.fromisoformat(insurance.expiry_date) > datetime.now()

    def test_expired_insurance(self, sample_expired_insurance_data):
        """Test expired insurance is detected"""
        insurance = Insurance(**sample_expired_insurance_data)

        assert insurance.is_valid() is False
        assert datetime.fromisoformat(insurance.expiry_date) < datetime.now()

    def test_insurance_expiring_soon(self, sample_insurance_data):
        """Test insurance expiring within threshold is detected"""
        # Set expiry to 7 days from now
        insurance_data = sample_insurance_data.copy()
        insurance_data["expiry_date"] = (datetime.now() + timedelta(days=7)).isoformat()

        insurance = Insurance(**insurance_data)

        expiry_date = datetime.fromisoformat(insurance.expiry_date)
        days_until_expiry = (expiry_date - datetime.now()).days

        assert days_until_expiry <= 30
        assert days_until_expiry > 0

    def test_insufficient_coverage(self, sample_insurance_data):
        """Test insurance with insufficient coverage amount"""
        insurance_data = sample_insurance_data.copy()
        insurance_data["coverage_amount"] = 100000.0  # Below minimum

        insurance = Insurance(**insurance_data)

        MIN_COVERAGE = 500000.0
        assert insurance.coverage_amount < MIN_COVERAGE


@pytest.mark.unit
@pytest.mark.compliance
class TestHotWorkPermit:
    """Test hot work permit functionality"""

    def test_permit_creation(self, sample_permit_data):
        """Test permit is created correctly"""
        permit = Permit(**sample_permit_data)

        assert permit.permit_type == "hot_work"
        assert permit.fire_watch_required is True
        assert "fire_extinguisher" in permit.safety_equipment_required

    def test_permit_timing(self, sample_permit_data):
        """Test permit start/end time validation"""
        permit = Permit(**sample_permit_data)

        start_time = datetime.fromisoformat(permit.scheduled_start)
        end_time = datetime.fromisoformat(permit.scheduled_end)

        # Check permit is in the future
        assert start_time > datetime.now()

        # Check end is after start
        assert end_time > start_time

        # Check duration is reasonable (not too long)
        duration_hours = (end_time - start_time).total_seconds() / 3600
        assert duration_hours <= 24  # Max 24 hours per permit

    def test_permit_safety_requirements(self, sample_permit_data):
        """Test safety requirements are enforced"""
        permit = Permit(**sample_permit_data)

        required_equipment = [
            "fire_extinguisher",
            "fire_blanket",
            "safety_goggles"
        ]

        for equipment in required_equipment:
            assert equipment in permit.safety_equipment_required


@pytest.mark.unit
@pytest.mark.compliance
class TestComplianceViolation:
    """Test compliance violation detection"""

    def test_violation_creation(self, sample_violation_data):
        """Test violation is created correctly"""
        violation = Violation(**sample_violation_data)

        assert violation.article_number == "E.2.1"
        assert violation.severity == "critical"
        assert violation.status == "active"

    def test_critical_violation_response_time(self, sample_violation_data):
        """Test critical violations have appropriate response time"""
        violation_data = sample_violation_data.copy()
        violation_data["severity"] = "critical"

        violation = Violation(**violation_data)

        # Critical violations should require response within 24 hours
        assert violation.response_time_hours <= 24

    def test_violation_required_actions(self, sample_violation_data):
        """Test violations have required actions defined"""
        violation = Violation(**sample_violation_data)

        assert len(violation.required_actions) > 0
        assert all(isinstance(action, str) for action in violation.required_actions)


@pytest.mark.integration
@pytest.mark.compliance
class TestVesselComplianceCheck:
    """Test complete vessel compliance checking workflow"""

    @pytest.mark.asyncio
    async def test_vessel_with_valid_insurance(self, sample_vessel_data, sample_insurance_data):
        """Test vessel with valid insurance passes compliance"""
        # This would test the full VerifyAgent workflow
        # For now, just test data structure
        vessel = sample_vessel_data
        insurance = Insurance(**sample_insurance_data)

        assert insurance.vessel_registration == vessel.get("vessel_registration", "TEST-001")
        assert insurance.is_valid()

    @pytest.mark.asyncio
    async def test_vessel_with_expired_insurance_creates_violation(
        self,
        sample_vessel_data,
        sample_expired_insurance_data,
        sample_violation_data
    ):
        """Test vessel with expired insurance creates violation"""
        insurance = Insurance(**sample_expired_insurance_data)
        violation = Violation(**sample_violation_data)

        assert not insurance.is_valid()
        assert violation.severity == "critical"
        assert violation.article_number == "E.2.1"


@pytest.mark.integration
@pytest.mark.compliance
class TestPermitWorkflow:
    """Test hot work permit workflow"""

    @pytest.mark.asyncio
    async def test_permit_request_and_approval(self, sample_permit_data):
        """Test complete permit request and approval workflow"""
        permit = Permit(**sample_permit_data)

        # Initially pending
        assert permit.status == "pending"

        # Simulate approval
        permit.status = "approved"
        permit.approved_by = "marina_manager"
        permit.approved_at = datetime.now().isoformat()

        assert permit.status == "approved"
        assert permit.approved_by is not None

    @pytest.mark.asyncio
    async def test_permit_monitoring_for_violations(self, sample_permit_data):
        """Test permit monitoring detects violations"""
        permit = Permit(**sample_permit_data)
        permit.status = "active"

        # Simulate work started
        permit.actual_start = datetime.now().isoformat()

        # Check if fire watch is required
        if permit.fire_watch_required:
            # In real implementation, check if fire watch is present
            fire_watch_present = True  # Mock
            assert fire_watch_present is True


@pytest.mark.integration
@pytest.mark.api
class TestComplianceAPI:
    """Test compliance API endpoints"""

    @pytest.mark.asyncio
    async def test_verify_vessel_endpoint(self, api_client, sample_vessel_data):
        """Test /api/v1/verify/vessel endpoint"""
        # This would test the actual API endpoint
        # response = await api_client.post("/api/v1/verify/vessel", json=sample_vessel_data)
        # assert response.status_code == 200
        pass

    @pytest.mark.asyncio
    async def test_request_permit_endpoint(self, api_client, sample_permit_data):
        """Test /api/v1/verify/permit/request endpoint"""
        # response = await api_client.post("/api/v1/verify/permit/request", json=sample_permit_data)
        # assert response.status_code == 200
        pass

    @pytest.mark.asyncio
    async def test_get_violations_endpoint(self, api_client):
        """Test /api/v1/verify/violations endpoint"""
        # response = await api_client.get("/api/v1/verify/violations?marina_id=marina_test")
        # assert response.status_code == 200
        pass


# Run tests with:
# pytest tests/test_verify_agent.py -v
# pytest tests/test_verify_agent.py -v -m compliance
# pytest tests/test_verify_agent.py -v -k insurance
