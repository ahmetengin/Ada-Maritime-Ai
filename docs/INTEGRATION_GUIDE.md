# Ada Maritime AI - Integration Guide

## Complete System Integration

This guide covers the complete Ada Maritime AI system integration, including the Big-5 Orchestrator for operations and the VERIFY Agent for security and compliance.

---

## System Architecture

```
Ada Maritime AI System
│
├── Big-5 Orchestrator (Operations)
│   ├── Berth Management
│   ├── Weather Services
│   ├── Maintenance Tracking
│   └── Analytics & Reporting
│
├── VERIFY Agent (Security & Compliance)
│   ├── Insurance Verification (Article E.2.1)
│   ├── Hot Work Permits (Article E.5.5)
│   ├── Compliance Checking (176 Articles)
│   └── Violation Management
│
└── Unified Orchestrator
    ├── Integrates both systems
    ├── Natural language processing
    ├── Routing & coordination
    └── Real-time monitoring
```

---

## Quick Start

### 1. Basic Usage

```python
from backend.main import AdaMaritimeAI

# Initialize system
ada = AdaMaritimeAI()

# Verify vessel for entry
result = await ada.verify_vessel_entry(
    vessel_name="Sea Dream",
    vessel_registration="TR-123456",
    marina_id="marina_001"
)

if result["entry_authorized"]:
    print("✅ Vessel authorized for entry")
else:
    print(f"❌ Entry denied: {result['violations']}")
```

### 2. Hot Work Permit

```python
# Request hot work permit
permit = await ada.request_hot_work_permit(
    work_description="Welding repairs on hull",
    work_location="Berth A12",
    scheduled_start="2025-11-12T10:00:00",
    scheduled_end="2025-11-12T16:00:00",
    requested_by="Captain Smith",
    requester_email="smith@vessel.com",
    requester_phone="+90 555 1234567",
    marina_id="marina_001"
)

print(f"Permit ID: {permit['permit_id']}")
print(f"Fire Watch Required: {permit['fire_watch_required']}")
```

### 3. Compliance Audit

```python
# Run daily audit
audit = await ada.run_compliance_audit("marina_001")

summary = audit["sections"]["summary"]
print(f"Total Violations: {summary['total_active_violations']}")
print(f"Critical Issues: {summary['by_severity']['critical']}")
```

---

## REST API

### Start API Server

```bash
# Development
cd backend
python -m uvicorn api:app --reload --port 8000

# Production
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints

#### Health Check
```http
GET /health
```

#### Vessel Verification
```http
POST /api/v1/verify/vessel
Content-Type: application/json

{
  "vessel_name": "Sea Dream",
  "vessel_registration": "TR-123456",
  "marina_id": "marina_001"
}
```

#### Hot Work Permit Request
```http
POST /api/v1/verify/permit/request
Content-Type: application/json

{
  "work_description": "Welding repairs",
  "work_location": "Berth A12",
  "scheduled_start": "2025-11-12T10:00:00",
  "scheduled_end": "2025-11-12T16:00:00",
  "requested_by": "Captain Smith",
  "requester_email": "smith@vessel.com",
  "requester_phone": "+90 555 1234567",
  "marina_id": "marina_001"
}
```

#### Get Active Permits
```http
GET /api/v1/verify/permit/active?marina_id=marina_001
```

#### Monitor Permit
```http
GET /api/v1/verify/permit/{permit_id}/monitor
```

#### Compliance Audit
```http
POST /api/v1/verify/audit
Content-Type: application/json

{
  "marina_id": "marina_001",
  "include_recommendations": true
}
```

#### Get Violations
```http
GET /api/v1/verify/violations?marina_id=marina_001&severity=critical
```

#### Resolve Violation
```http
POST /api/v1/verify/violations/{violation_id}/resolve
Content-Type: application/json

{
  "violation_id": "viol_123",
  "resolved_by": "marina_manager",
  "resolution_notes": "Insurance policy renewed"
}
```

#### Dashboard
```http
GET /api/v1/dashboard/marina_001
```

---

## Python Integration Examples

### Example 1: Complete Vessel Entry Workflow

```python
from backend.main import AdaMaritimeAI
from datetime import datetime

async def process_vessel_arrival():
    ada = AdaMaritimeAI()

    # Step 1: Verify compliance
    verification = await ada.verify_vessel_entry(
        vessel_name="Ocean Star",
        vessel_registration="GR-789012",
        marina_id="marina_001",
        booking_id="book_456"
    )

    if not verification["entry_authorized"]:
        print("❌ Entry denied")
        print(f"Violations: {verification['violations']}")
        print(f"Actions required: {verification['required_actions']}")
        return False

    # Step 2: Check for any work requirements
    # If work is needed, request permit

    # Step 3: Assign berth (would integrate with Big-5)

    print("✅ Vessel processed successfully")
    return True
```

### Example 2: Daily Operations Monitor

```python
async def daily_operations_monitor():
    ada = AdaMaritimeAI()
    marina_id = "marina_001"

    # Run compliance audit
    audit = await ada.run_compliance_audit(marina_id)

    # Get dashboard
    dashboard = ada.get_dashboard(marina_id)

    # Check critical issues
    if dashboard["critical_issues"]:
        print("⚠️  CRITICAL ISSUES DETECTED")
        for issue in dashboard["critical_issues"]:
            print(f"  - Article {issue['article']}: {issue['description']}")
            # Send alert to management

    # Check expiring insurance
    insurance_skill = ada.orchestrator.verify.skills["insurance_verification"]
    expiring = await insurance_skill.execute({
        "operation": "check_expiry",
        "marina_id": marina_id,
        "days_threshold": 7  # 7 days warning
    })

    if expiring["expired_count"] > 0:
        print(f"⚠️  {expiring['expired_count']} vessels with expired insurance!")
        # Take action

    if expiring["expiring_soon_count"] > 0:
        print(f"📧 Sending renewal reminders to {expiring['expiring_soon_count']} vessels")
        # Send reminders
```

### Example 3: Hot Work Safety Monitoring

```python
async def monitor_hot_work_safety():
    ada = AdaMaritimeAI()
    permit_skill = ada.orchestrator.verify.skills["hot_work_monitoring"]

    # Get all active permits
    active = await permit_skill.execute({
        "operation": "check_active",
        "marina_id": "marina_001"
    })

    print(f"Active hot work permits: {active['active_permits_count']}")

    # Monitor each active permit
    for permit in active["active_permits"]:
        monitor = await permit_skill.execute({
            "operation": "monitor",
            "permit_id": permit["permit_id"]
        })

        if not monitor["is_compliant"]:
            print(f"⚠️  VIOLATION at {permit['work_location']}")
            print(f"   Violations: {monitor['violations']}")
            # Stop work immediately
            # Notify marina management
            # Log incident
```

---

## Unified Orchestrator Features

### Natural Language Processing

The Unified Orchestrator can process natural language requests and route them appropriately:

```python
async def handle_user_request(user_input: str):
    ada = AdaMaritimeAI()

    result = await ada.process_request(
        user_input="Check insurance status for all vessels in marina",
        user_id="admin_001",
        marina_id="marina_001"
    )

    print(f"Intent: {result['intent']}")
    print(f"Orchestrator: {result['recommended_orchestrator']}")
    # Result routes to 'verify' for compliance-related request
```

### Automatic Routing

Requests are automatically routed based on keywords:

- **Compliance/Security Keywords**: insurance, permit, compliance, violation, safety, fire watch, hot work, audit, regulation, article
  → Routes to **VERIFY Agent**

- **Operational Keywords**: berth, booking, weather, maintenance, availability, search
  → Routes to **Big-5 Orchestrator**

---

## Integration with Existing Systems

### Database Integration

```python
from backend.database import get_database
from backend.main import AdaMaritimeAI

ada = AdaMaritimeAI()
db = get_database()

# Sync insurance data from database
vessels = db.get_all_vessels()
for vessel in vessels:
    insurance = db.get_insurance(vessel.id)
    if insurance:
        # Register in VERIFY system
        await ada.orchestrator.verify.skills["insurance_verification"].execute({
            "operation": "register",
            "vessel_name": vessel.name,
            "vessel_registration": vessel.registration,
            ...
        })
```

### Event-Driven Integration

```python
# Listen for events and trigger compliance checks
from backend.events import EventBus

event_bus = EventBus()

@event_bus.on("vessel.arrived")
async def on_vessel_arrival(event):
    ada = AdaMaritimeAI()

    # Verify compliance
    result = await ada.verify_vessel_entry(
        vessel_name=event.vessel_name,
        vessel_registration=event.vessel_registration,
        marina_id=event.marina_id
    )

    if not result["entry_authorized"]:
        event_bus.emit("vessel.entry_denied", result)
    else:
        event_bus.emit("vessel.entry_authorized", result)


@event_bus.on("permit.requested")
async def on_permit_requested(event):
    ada = AdaMaritimeAI()

    permit = await ada.request_hot_work_permit(**event.data)
    event_bus.emit("permit.created", permit)
```

---

## Scheduled Tasks

### Daily Compliance Audit

```python
import asyncio
import schedule

async def daily_audit_job():
    ada = AdaMaritimeAI()
    marinas = ["marina_001", "marina_002", "marina_003"]

    for marina_id in marinas:
        print(f"\n🔍 Auditing {marina_id}...")

        audit = await ada.run_compliance_audit(marina_id)

        # Generate and email report
        # Store results
        # Alert on critical issues

# Schedule daily at 6 AM
schedule.every().day.at("06:00").do(lambda: asyncio.run(daily_audit_job()))
```

### Insurance Expiry Check

```python
async def check_insurance_expiry():
    ada = AdaMaritimeAI()

    insurance_skill = ada.orchestrator.verify.skills["insurance_verification"]

    result = await insurance_skill.execute({
        "operation": "check_expiry",
        "days_threshold": 30
    })

    # Send renewal reminders
    for policy in result["expiring_soon_policies"]:
        # Email vessel owner
        send_email(
            to=policy["vessel_owner_email"],
            subject="Insurance Renewal Reminder",
            body=f"Your insurance expires in {policy['days_until_expiry']} days"
        )

# Check weekly on Monday
schedule.every().monday.at("08:00").do(lambda: asyncio.run(check_insurance_expiry()))
```

---

## Monitoring & Observability

### Logging

All operations are logged with full context:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ada_maritime.log"),
        logging.StreamHandler()
    ]
)
```

### Metrics

Track key metrics:

```python
from prometheus_client import Counter, Histogram

# Define metrics
vessel_entries = Counter('vessel_entries_total', 'Total vessel entries')
vessel_denials = Counter('vessel_denials_total', 'Total entry denials')
permit_requests = Counter('permit_requests_total', 'Total permit requests')
violations_detected = Counter('violations_total', 'Total violations')

# Use in code
async def verify_vessel(...):
    vessel_entries.inc()

    result = await ada.verify_vessel_entry(...)

    if not result["entry_authorized"]:
        vessel_denials.inc()
```

---

## Security Best Practices

### Authentication & Authorization

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/v1/verify/permit/approve")
async def approve_permit(
    permit_id: str,
    token: str = Security(security)
):
    # Verify token
    user = verify_token(token)

    # Check authorization
    if not user.has_permission("approve_permits"):
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Approve permit
    ...
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/verify/vessel")
@limiter.limit("10/minute")
async def verify_vessel(request: Request, ...):
    ...
```

---

## Testing

### Unit Tests

```python
import pytest
from backend.main import AdaMaritimeAI

@pytest.mark.asyncio
async def test_vessel_verification():
    ada = AdaMaritimeAI()

    result = await ada.verify_vessel_entry(
        vessel_name="Test Vessel",
        vessel_registration="TEST-001",
        marina_id="marina_test"
    )

    assert "entry_authorized" in result
    assert "violations" in result
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_hot_work_workflow():
    ada = AdaMaritimeAI()

    # Request permit
    permit = await ada.request_hot_work_permit(...)
    assert permit["success"]

    # Monitor permit
    permit_skill = ada.orchestrator.verify.skills["hot_work_monitoring"]
    monitor = await permit_skill.execute({
        "operation": "monitor",
        "permit_id": permit["permit_id"]
    })

    assert monitor["is_compliant"]
```

---

## Troubleshooting

### Common Issues

**Issue**: Insurance skill not found
```python
# Solution: Ensure skills are registered
ada = AdaMaritimeAI()
print(ada.orchestrator.get_all_available_skills())
```

**Issue**: API Key not found
```python
# Solution: Set environment variable
export ANTHROPIC_API_KEY="your-key-here"

# Or pass directly
ada = AdaMaritimeAI(api_key="your-key-here")
```

**Issue**: Database connection error
```python
# Solution: Check database configuration
from backend.config import get_config
config = get_config()
print(config.database.connection_string)
```

---

## Performance Optimization

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_compliance_rules(category: str):
    # Cache rules to avoid repeated loading
    return load_rules(category)
```

### Async Batch Processing

```python
async def process_multiple_vessels(vessels: List[str]):
    ada = AdaMaritimeAI()

    # Process all vessels concurrently
    tasks = [
        ada.verify_vessel_entry(v["name"], v["registration"], v["marina_id"])
        for v in vessels
    ]

    results = await asyncio.gather(*tasks)
    return results
```

---

## Support

- **Documentation**: `/docs/VERIFY_AGENT.md`
- **API Documentation**: `http://localhost:8000/docs` (when running)
- **Examples**: `/backend/orchestrator/verify_agent_example.py`
- **Integration Examples**: `/backend/main.py`

---

**Version**: 1.0.0
**Last Updated**: 2025-11-11
**Status**: Production Ready
