# VERIFY Agent - Security Management & Compliance System

## Overview

The VERIFY Agent is a comprehensive security management and compliance verification system for Ada Maritime AI. It implements automated monitoring and enforcement of the 176-article marina operation regulations based on West Istanbul Marina standards.

## Features

### Core Capabilities

- **176-Article Compliance System**: Comprehensive rule-based compliance checking across all operational categories
- **Insurance Verification (Article E.2.1)**: Automated yacht insurance validation and monitoring
- **Hot Work Permit Management (Article E.5.5)**: Safety-critical permit workflow for welding, grinding, and other hot work
- **Violation Detection & Logging**: Real-time violation detection with severity-based escalation
- **Security Incident Management**: Tracking and response coordination for security events
- **Compliance Auditing**: Automated and on-demand compliance audits with recommendations

### Compliance Categories

1. **Safety**: Fire prevention, accident prevention, emergency procedures
2. **Environmental**: Waste disposal, pollution prevention, hazardous materials
3. **Insurance & Liability**: Coverage requirements, policy verification
4. **Permits & Licenses**: Work permits, authorization, documentation
5. **Operational**: Navigation, mooring, launching, lifting procedures
6. **Administrative**: Documentation, contracts, payments, reservations
7. **Security**: Access control, entry authorization, surveillance

## Architecture

### Components

```
VERIFY Agent
├── verify_agent.py              # Main agent orchestrator
├── compliance_rules.json         # 176-article configuration
├── Skills
│   ├── insurance_verification_skill.py    # Article E.2.1
│   ├── hot_work_permit_skill.py          # Article E.5.5
│   └── compliance_checking_skill.py       # Full system
└── Models
    ├── Insurance                 # Insurance records
    ├── Permit                    # Permit records
    ├── Violation                 # Violation tracking
    ├── ComplianceRule            # Rule definitions
    ├── SecurityIncident          # Security events
    └── Document                  # Document verification
```

## Key Articles

### Article E.2.1 - Insurance Requirements

**Rule**: All yachts must have valid Third-Party Financial Liability insurance

**Requirements**:
- Minimum coverage: EUR 1,000,000
- Must be from approved insurance provider
- Policy document must be submitted before mooring
- Policy must be valid (not expired)

**Enforcement**:
- Contract automatically cancelled if insurance expires
- Yacht removed from marina if non-compliant
- All removal costs borne by yacht owner

**Example**:
```python
from verify_agent import VerifyAgent

agent = VerifyAgent()

# Verify insurance
result = await agent.verify_insurance(
    vessel_name="Sea Dream",
    vessel_registration="TR-123456",
    marina_id="marina_001"
)

if not result["insurance_valid"]:
    print(f"Violations: {result['violations']}")
    print(f"Marina Entry: {result['marina_entry_permitted']}")
```

### Article E.5.5 - Hot Work Safety

**Rule**: Hot work (welding, grinding, sanding, etc.) requires safety measures

**Requirements**:
- Approved permit required before work starts
- Fire watch must be present during work
- Safety equipment must be in place
- Nearby vessels must be protected
- Work stopped immediately if violations detected

**Enforcement**:
- Work interrupted immediately if violations found
- Detailed damage report created
- Yacht owner liable for all damages
- Potential marina access ban

**Example**:
```python
from skills.hot_work_permit_skill import HotWorkPermitSkill

skill = HotWorkPermitSkill()

# Request permit
result = await skill.execute({
    "operation": "request",
    "work_description": "Welding repairs on hull",
    "work_location": "Berth A12",
    "scheduled_start": "2025-11-12T10:00:00",
    "scheduled_end": "2025-11-12T16:00:00",
    ...
})

# Monitor compliance
monitor = await skill.execute({
    "operation": "monitor",
    "permit_id": result["permit_id"]
})
```

## Usage

### Initialize VERIFY Agent

```python
from backend.orchestrator.verify_agent import VerifyAgent, VerifyContext
from backend.skills.insurance_verification_skill import InsuranceVerificationSkill
from backend.skills.hot_work_permit_skill import HotWorkPermitSkill
from backend.skills.compliance_checking_skill import ComplianceCheckingSkill

# Initialize agent
agent = VerifyAgent()

# Register skills
agent.register_skill("insurance_verification", InsuranceVerificationSkill())
agent.register_skill("hot_work_monitoring", HotWorkPermitSkill())
agent.register_skill("compliance_checking", ComplianceCheckingSkill())
```

### Run Compliance Audit

```python
# Create context
context = VerifyContext(
    marina_id="marina_001",
    user_id="admin_001",
    session_id="audit_session_001",
    check_scope="all"
)

# Run audit
audit_result = agent.run_compliance_audit(context)

print(f"Compliance Rate: {audit_result['compliance_rate']}%")
print(f"Violations: {audit_result['total_violations']}")
print(f"Critical Issues: {len(audit_result['critical_issues'])}")
```

### Check Specific Rule

```python
# Check insurance compliance for a vessel
check_result = agent.check_compliance(
    rule_id="E.2.1",
    entity_type="vessel",
    entity_id="TR-123456",
    entity_data={
        "insurance_valid": True,
        "coverage_amount": 2000000,
        "policy_expires": "2026-01-01"
    },
    context=context
)

if not check_result.passed:
    print(f"Violations: {check_result.violations_detected}")
```

### Manage Violations

```python
# Get active violations
violations = agent.get_active_violations(
    marina_id="marina_001",
    severity="critical"
)

# Resolve violation
agent.resolve_violation(
    violation_id="viol_123",
    resolved_by="marina_manager",
    resolution_notes="Insurance policy renewed"
)

# Get compliance summary
summary = agent.get_compliance_summary("marina_001")
print(f"Active Violations: {summary['total_active_violations']}")
```

## Skills

### Insurance Verification Skill

**Operations**:
- `verify`: Check insurance validity
- `register`: Register new insurance policy
- `check_expiry`: Find expiring policies
- `get_status`: Get insurance status

**Example**:
```python
from skills.insurance_verification_skill import InsuranceVerificationSkill

skill = InsuranceVerificationSkill()

# Register insurance
await skill.execute({
    "operation": "register",
    "vessel_name": "Sea Dream",
    "policy_number": "INS-2024-001",
    "provider": "Allianz",
    "coverage_amount": 2000000,
    ...
})

# Check expiring policies
await skill.execute({
    "operation": "check_expiry",
    "marina_id": "marina_001",
    "days_threshold": 30
})
```

### Hot Work Permit Skill

**Operations**:
- `request`: Request hot work permit
- `approve`: Approve permit
- `monitor`: Monitor active permit
- `complete`: Mark permit as completed
- `check_active`: List active permits
- `violation_check`: Check for violations

**Example**:
```python
from skills.hot_work_permit_skill import HotWorkPermitSkill

skill = HotWorkPermitSkill()

# Request permit
permit = await skill.execute({
    "operation": "request",
    "work_description": "Welding repairs",
    ...
})

# Approve
await skill.execute({
    "operation": "approve",
    "permit_id": permit["permit_id"],
    "approved_by": "Marina Manager"
})

# Monitor
await skill.execute({
    "operation": "monitor",
    "permit_id": permit["permit_id"]
})
```

### Compliance Checking Skill

**Operations**:
- `check`: Check specific article/entity
- `audit`: Comprehensive audit
- `get_rules`: Get rule definitions
- `check_category`: Check category compliance
- `get_summary`: Get compliance summary

**Example**:
```python
from skills.compliance_checking_skill import ComplianceCheckingSkill

skill = ComplianceCheckingSkill()

# Comprehensive audit
audit = await skill.execute({
    "operation": "audit",
    "marina_id": "marina_001",
    "include_recommendations": True
})

# Check specific category
safety = await skill.execute({
    "operation": "check_category",
    "category": "safety",
    "marina_id": "marina_001"
})
```

## Data Models

### Insurance

```python
Insurance(
    insurance_id: str
    vessel_name: str
    vessel_registration: str
    policy_number: str
    insurance_type: str  # liability, hull, comprehensive, etc.
    provider: str
    coverage_amount: float
    currency: str
    issue_date: str
    expiry_date: str
    status: str  # valid, expired, pending, rejected
    document_url: Optional[str]
)
```

### Permit

```python
Permit(
    permit_id: str
    permit_type: str  # hot_work, cold_work, diving, etc.
    marina_id: str
    work_description: str
    work_location: str
    scheduled_start: str
    scheduled_end: str
    status: str  # requested, approved, active, completed, expired
    fire_watch_required: bool
    fire_watch_personnel: Optional[str]
    safety_equipment_required: List[str]
    conditions: List[str]
)
```

### Violation

```python
Violation(
    violation_id: str
    rule_id: str
    article_number: str
    marina_id: str
    violation_type: str  # safety, environmental, insurance, permit
    severity: str  # low, medium, high, critical
    detected_at: str
    description: str
    status: str  # detected, notified, in_resolution, resolved, escalated
    entity_type: str  # vessel, berth, marina, staff
    entity_id: str
    vessel_name: Optional[str]
    resolution_notes: Optional[str]
)
```

## Compliance Rules Configuration

Located at: `backend/config/compliance_rules.json`

```json
{
  "compliance_system": {
    "name": "Marina 176-Article Compliance System",
    "version": "1.0.0"
  },
  "rules": [
    {
      "rule_id": "E.2.1",
      "article_number": "E.2.1",
      "title": "Third-Party Financial Liability Insurance Requirement",
      "category": "insurance_and_liability",
      "severity": "critical",
      "auto_check": true,
      "check_frequency_hours": 24,
      ...
    }
  ]
}
```

## Severity Levels

- **Low**: Minor violations with minimal impact (72h response)
- **Medium**: Moderate violations requiring attention (24h response)
- **High**: Serious violations requiring immediate action (4h response)
- **Critical**: Critical violations posing immediate danger (1h response)

## Integration with Big-5 Orchestrator

The VERIFY Agent integrates with the main Big-5 Orchestrator:

```python
from backend.orchestrator.big5_orchestrator import Big5Orchestrator
from backend.orchestrator.verify_agent import VerifyAgent

# Initialize both orchestrators
big5 = Big5Orchestrator()
verify = VerifyAgent()

# Register VERIFY skills with Big-5
for skill_name, skill_handler in verify.skills.items():
    big5.register_skill(f"verify_{skill_name}", skill_handler)
```

## Monitoring & Alerts

### Real-Time Monitoring

```python
# Monitor all active permits
active_permits = await agent.skills["hot_work_monitoring"].execute({
    "operation": "check_active",
    "marina_id": "marina_001"
})

# Check for violations
violations = await agent.skills["hot_work_monitoring"].execute({
    "operation": "violation_check",
    "marina_id": "marina_001"
})
```

### Automated Alerts

- Critical violations trigger immediate notifications
- Email alerts sent to marina management
- Escalation if violations not resolved within threshold
- Daily compliance summary reports

## Testing

Run the example file to test all features:

```bash
cd backend/orchestrator
python verify_agent_example.py
```

This will demonstrate:
1. Insurance verification workflow
2. Hot work permit management
3. Comprehensive compliance audit
4. Violation detection and management
5. Complete integration workflow

## Future Enhancements

- [ ] Machine learning for violation prediction
- [ ] Mobile app for permit requests
- [ ] Real-time IoT sensor integration
- [ ] Blockchain-based compliance certificates
- [ ] AI-powered risk assessment
- [ ] Automated penalty calculation
- [ ] Integration with harbormaster systems
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] External API for compliance reporting

## References

- West Istanbul Marina Operation Regulations
- Turkish Maritime Law
- ISO 9001:2015 Quality Management
- Blue Flag Marina Standards
- IMO Safety Regulations

## Support

For questions or issues:
- Documentation: `/docs/VERIFY_AGENT.md`
- Examples: `/backend/orchestrator/verify_agent_example.py`
- Configuration: `/backend/config/compliance_rules.json`
- GitHub Issues: https://github.com/ahmetengin/Ada-Maritime-Ai/issues

---

**Version**: 1.0.0
**Last Updated**: 2025-11-11
**Status**: Production Ready
