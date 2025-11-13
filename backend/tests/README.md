# Ada Maritime AI - Test Suite

Comprehensive test suite for Ada Maritime AI system.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_verify_agent.py     # VERIFY Agent tests
├── test_vhf_monitoring.py   # VHF monitoring tests
├── test_api.py              # API endpoint tests
├── test_database.py         # Database tests
├── test_auth.py             # Authentication tests
└── README.md                # This file
```

## Running Tests

### Run all tests
```bash
cd backend
pytest
```

### Run specific test file
```bash
pytest tests/test_verify_agent.py -v
```

### Run tests by marker
```bash
# Unit tests only
pytest -m unit

# Compliance tests
pytest -m compliance

# VHF monitoring tests
pytest -m vhf

# Integration tests
pytest -m integration

# API tests
pytest -m api
```

### Run tests by keyword
```bash
# All insurance tests
pytest -k insurance

# All permit tests
pytest -k permit

# All violation tests
pytest -k violation
```

### Run with coverage
```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run slow tests
```bash
# Include slow tests (SDR, API calls)
pytest --slow
```

## Test Markers

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (slower, may need databases)
- `@pytest.mark.slow` - Slow tests (SDR scanning, real API calls)
- `@pytest.mark.compliance` - VERIFY Agent compliance tests
- `@pytest.mark.vhf` - VHF monitoring tests
- `@pytest.mark.database` - Database tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.auth` - Authentication tests

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `sample_vessel_data` - Mock vessel data
- `sample_insurance_data` - Mock valid insurance
- `sample_expired_insurance_data` - Mock expired insurance
- `sample_permit_data` - Mock hot work permit
- `sample_violation_data` - Mock compliance violation
- `sample_vhf_communication` - Mock VHF communication
- `sample_marina_config` - Mock marina configuration
- `mock_anthropic_api` - Mock Anthropic API calls
- `test_database` - Test database setup/teardown
- `api_client` - FastAPI test client

## Writing Tests

### Unit Test Example

```python
import pytest

@pytest.mark.unit
@pytest.mark.compliance
def test_insurance_validation(sample_insurance_data):
    """Test insurance validation logic"""
    insurance = Insurance(**sample_insurance_data)
    assert insurance.is_valid()
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_verify_vessel_endpoint(api_client, sample_vessel_data):
    """Test vessel verification API endpoint"""
    response = await api_client.post(
        "/api/v1/verify/vessel",
        json=sample_vessel_data
    )
    assert response.status_code == 200
    assert response.json()["entry_authorized"] is True
```

### Using Fixtures

```python
def test_with_fixtures(sample_vessel_data, sample_insurance_data):
    """Test using multiple fixtures"""
    vessel = sample_vessel_data
    insurance = Insurance(**sample_insurance_data)
    assert insurance.vessel_name == vessel["vessel_name"]
```

## Coverage Requirements

- Minimum coverage: 70%
- Target coverage: 85%
- Critical modules (VERIFY Agent, auth): 90%+

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Scheduled daily runs

## Test Data

Test data should:
- Use realistic values
- Be deterministic (no random data)
- Be isolated (no shared state between tests)
- Clean up after themselves

## Mocking

Mock external services:
- Anthropic API calls
- Email sending
- SDR hardware
- Database (for unit tests)

Example:
```python
@pytest.fixture
def mock_email_service(monkeypatch):
    def mock_send_email(*args, **kwargs):
        return True
    monkeypatch.setattr(
        "backend.notifications.email_service.EmailService.send_email",
        mock_send_email
    )
```

## Debugging Tests

### Run with verbose output
```bash
pytest -vv
```

### Show print statements
```bash
pytest -s
```

### Stop on first failure
```bash
pytest -x
```

### Drop into debugger on failure
```bash
pytest --pdb
```

### Run specific test
```bash
pytest tests/test_verify_agent.py::TestInsuranceVerification::test_valid_insurance
```

## Performance Testing

For performance tests, use pytest-benchmark:

```python
def test_insurance_verification_performance(benchmark, sample_insurance_data):
    """Test insurance verification performance"""
    insurance = Insurance(**sample_insurance_data)
    result = benchmark(insurance.is_valid)
    assert result is True
```

Run with:
```bash
pytest --benchmark-only
```

## Test Reports

Generate test reports:

```bash
# HTML report
pytest --html=report.html --self-contained-html

# JUnit XML (for CI)
pytest --junitxml=junit.xml
```

## Best Practices

1. **One assertion per test** (when possible)
2. **Clear test names** describing what is tested
3. **Arrange-Act-Assert** pattern
4. **Use fixtures** for common setup
5. **Mock external dependencies**
6. **Test edge cases** and error conditions
7. **Keep tests fast** (< 1 second for unit tests)
8. **Clean up after tests**

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Meet coverage requirements
4. Update test documentation

## Support

For test issues:
- Check test logs
- Review fixtures in conftest.py
- Verify test data
- Check mocking configuration
