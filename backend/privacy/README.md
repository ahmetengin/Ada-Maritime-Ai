# Ada.Sea Privacy Module

🔒 **Zero-Trust, Privacy-First Architecture for Maritime AI**

## Overview

The Ada.Sea Privacy Module implements a comprehensive privacy-first architecture where the captain has complete control over all data. Built on principles of zero trust, explicit consent, and regulatory compliance (KVKK/GDPR).

## Quick Start

```python
from backend.privacy import AdaSeaPrivacyCore, DataClassification

# Initialize privacy core
privacy = AdaSeaPrivacyCore(captain_id="boss@ada.sea")

# Attempt to share data (requires captain approval)
result = await privacy.share_data(
    destination="Yalikavak Marina",
    data={'vessel_length': 65, 'arrival_time': '2025-11-13T14:00:00Z'},
    data_type=DataClassification.VESSEL_SPECIFICATIONS.value,
    purpose="berth_reservation"
)

# Check if captain approval required
if not result['success'] and 'voice_prompt' in result:
    print(result['voice_prompt'])
    # Display voice prompt to captain for approval
```

## Module Structure

```
privacy/
├── __init__.py                 # Module exports
├── privacy_core.py            # Core privacy orchestration
├── data_policy.py             # Data classification & permissions
├── consent_manager.py         # Captain consent handling
├── audit_log.py              # Audit trail & transparency
├── marina_integration.py     # Ada.Marina integration
├── compliance.py             # KVKK & GDPR compliance
└── README.md                 # This file
```

## Core Components

### 1. AdaSeaPrivacyCore

Main privacy orchestration system.

**Key Features:**
- Zero trust by default
- Explicit consent required for all transfers
- Complete audit trail
- Captain voice control

**Usage:**
```python
privacy = AdaSeaPrivacyCore(captain_id="boss@ada.sea")

# Share data with approval
result = await privacy.share_data(...)

# Get audit trail
trail = privacy.get_audit_trail(hours=168)

# Get privacy status
status = privacy.get_privacy_status()

# Revoke permissions
count = privacy.revoke_all_permissions()
```

### 2. DataPolicy

Granular data classification system.

**Permission Levels:**
- `PRIVATE`: Never share without explicit command
- `RESTRICTED`: Essential data only, with approval
- `CONDITIONAL`: Captain consent required
- `ANONYMOUS`: No vessel identification

**Usage:**
```python
from backend.privacy import DataPolicy, DataClassification

policy = DataPolicy()

# Check permission level
level = policy.get_permission_level(DataClassification.GPS_HISTORY)
# Returns: PermissionLevel.PRIVATE

# Get minimal data for purpose
minimal = policy.get_minimal_data_for_purpose('berth_reservation')
# Returns: [VESSEL_SPECIFICATIONS, ARRIVAL_TIME]
```

### 3. ConsentManager

Handle captain approvals and standing permissions.

**Usage:**
```python
manager = ConsentManager()

# Create consent request
request = await manager.request_captain_permission(
    destination="Ada.marina:Yalikavak",
    data_type="vessel_specifications",
    data_size=256,
    purpose="berth_assignment"
)

# Process captain response
consent = await manager.process_captain_response(
    request_id=request.request_id,
    granted=True,
    captain_id="boss@ada.sea",
    method=ConsentMethod.VOICE,
    confirmation_text="Evet paylaş"
)

# Check standing permission
standing = manager.check_standing_permission(
    destination="Ada.marina:Yalikavak",
    data_type="vessel_specifications"
)
```

### 4. AuditLog

Complete transparency and tamper-proof logging.

**Usage:**
```python
audit = AuditLog()

# Log transfer
entry = audit.log_transfer(
    destination="Yalikavak Marina",
    data_type="vessel_specifications",
    captain_id="boss@ada.sea",
    authorization_method="voice_confirmed",
    result="success",
    data={'vessel_length': 65}
)

# Query audit trail
entries = audit.query(captain_id="boss@ada.sea", hours=168)

# Get summary
summary = audit.get_summary("boss@ada.sea", hours=168)

# Export for captain
report = audit.export_for_captain(
    captain_id="boss@ada.sea",
    format="human"  # or "json"
)
```

### 5. AdaMarinaIntegration

Trust boundary enforcement for Ada.Marina ecosystem.

**Usage:**
```python
integration = AdaMarinaIntegration(privacy_core)

# Request berth assignment
result = await integration.request_berth_assignment(
    marina_id="yalikavak",
    vessel_specs={'length': 65, 'beam': 18, 'draft': 3},
    arrival_time="2025-11-13T14:00:00Z"
)

# Check-in to marina
result = await integration.inform_arrival(
    marina_id="yalikavak",
    vessel_name="Phisedelia",
    current_position={'lat': 37.1234, 'lon': 27.5678},
    berth_number="C-42"
)

# Emergency notification (bypass consent)
result = await integration.emergency_notification(
    marina_id="yalikavak",
    emergency_type="fire",
    vessel_info={...},
    position={...}
)
```

### 6. Compliance (KVKK/GDPR)

Regulatory compliance framework.

**Usage:**
```python
# KVKK (Turkish Law)
from backend.privacy import KVKKCompliance

kvkk = KVKKCompliance()

# Handle data subject request
result = kvkk.handle_data_subject_request(
    request_type='bilgi_talep',  # Access request
    captain_id='boss@ada.sea'
)

# Generate privacy notice
notice = kvkk.framework.generate_privacy_notice(language='tr')

# GDPR (EU)
from backend.privacy import GDPRCompliance

gdpr = GDPRCompliance()

# Validate legal basis
validation = gdpr.validate_legal_basis({
    'purpose': 'berth_reservation',
    'consent': True
})

# Conduct DPIA
dpia = gdpr.conduct_dpia({
    'type': 'data_transfer',
    'data_type': 'vessel_specifications'
})
```

## Voice Commands

### Data Sharing Control (Turkish)

```
"Ada, veri paylaşım geçmişini göster"
"Ada, hangi bilgileri kimle paylaştım?"
"Ada, Yalikavak Marina'ya ne gönderdin?"
"Ada, tüm otomatik paylaşımları iptal et"
"Ada, marina izinlerini göster"
```

### KVKK Rights (Turkish)

```
"Ada, verilerimi göster"           # Right to access
"Ada, [veri]'yi düzelt"            # Right to rectification
"Ada, [veri]'yi sil"               # Right to erasure
"Ada, [veri] paylaşımını durdur"   # Right to restriction
"Ada, verilerimi dışa aktar"       # Right to portability
"Ada, [işleme] itiraz ediyorum"    # Right to object
```

## Data Flow

```
┌──────────────┐
│   Captain    │
│   Request    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  AdaSeaPrivacyCore  │
├──────────────────────┤
│ 1. Check Data Policy │
│ 2. Check Standing    │
│ 3. Request Consent   │
│ 4. Filter Data       │
│ 5. Execute Transfer  │
│ 6. Log Audit Entry   │
└──────┬───────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ Destination │   │  Audit Log  │
│  (Marina)   │   │  (Local DB) │
└─────────────┘   └─────────────┘
```

## Security

### Encryption
- **At Rest**: AES-256-GCM
- **In Transit**: TLS 1.3 + mTLS
- **Backups**: Zero-knowledge (client-side only)

### Access Control
- Captain authentication required
- Voice signature verification
- Biometric authentication (future)
- Session timeouts

### Audit
- Tamper-proof logging
- Data integrity hashing
- Complete transfer history
- Real-time notifications

## Compliance

### KVKK (Turkish Law 6698)
- ✅ Explicit consent (Article 3)
- ✅ Data subject rights (Article 11)
- ✅ Purpose limitation
- ✅ Data minimization
- ✅ Storage limitation
- ✅ Accountability

### GDPR (EU 2016/679)
- ✅ Lawfulness, fairness, transparency (Article 5)
- ✅ Data subject rights (Articles 15-22)
- ✅ Privacy by Design (Article 25)
- ✅ Privacy by Default (Article 25)
- ✅ DPIA (Article 35)
- ✅ Breach notification (Articles 33-34)

## Testing

```bash
# Unit tests
python -m pytest privacy/tests/test_privacy_core.py
python -m pytest privacy/tests/test_consent_manager.py
python -m pytest privacy/tests/test_audit_log.py

# Integration tests
python -m pytest tests/integration/test_privacy_flow.py

# Compliance validation
python -m privacy.compliance validate --framework=kvkk
python -m privacy.compliance validate --framework=gdpr
```

## Configuration

### Default Settings

```python
privacy = AdaSeaPrivacyCore(
    captain_id="boss@ada.sea",
    data_policy=None,  # Uses default secure policy
    audit_log_path=None  # ~/.ada_sea/audit_log.db
)

# Settings
privacy.zero_trust_mode = True  # Default: True
privacy.captain_auth_required = True  # Default: True
privacy.cloud_sync_enabled = False  # Default: False
```

### Custom Data Policy

```python
from backend.privacy import DataPolicy, DataClassification, PermissionLevel

# Create custom policy
custom_policy = DataPolicy()
custom_policy.classification_map[DataClassification.FUEL_CONSUMPTION_STATS] = PermissionLevel.ANONYMOUS

privacy = AdaSeaPrivacyCore(
    captain_id="boss@ada.sea",
    data_policy=custom_policy
)
```

## Examples

### Example 1: Marina Berth Reservation

```python
# Initialize
privacy = AdaSeaPrivacyCore(captain_id="boss@ada.sea")

# Request berth
result = await privacy.share_data(
    destination="Ada.marina:Yalikavak",
    data={
        'vessel_length': 65,
        'vessel_beam': 18,
        'vessel_draft': 3,
        'arrival_time': '2025-11-13T14:00:00Z'
    },
    data_type=DataClassification.VESSEL_SPECIFICATIONS.value,
    purpose="berth_reservation"
)

# Captain approves via voice
consent = await privacy.process_captain_consent(
    request_id=result['request']['request_id'],
    granted=True,
    method=ConsentMethod.VOICE,
    confirmation_text="Evet paylaş"
)

# Transfer executes automatically after approval
# Audit entry created automatically
```

### Example 2: Review Data Sharing History

```python
# Get summary
summary = privacy.get_sharing_summary(hours=168)
print(f"Last 7 days: {summary['total_transfers']} transfers")

# Get detailed audit trail
trail = privacy.get_audit_trail(hours=168)
for entry in trail:
    print(f"{entry['timestamp']}: {entry['destination']} - {entry['data_type']}")

# Export for captain review
report = privacy.export_privacy_data(format="human")
print(report)
```

### Example 3: Emergency Bypass

```python
# Emergency - bypass consent (heavily logged)
result = await privacy.share_data(
    destination="Coast Guard",
    data={
        'vessel_name': 'Phisedelia',
        'position': {'lat': 37.1234, 'lon': 27.5678},
        'emergency_type': 'fire'
    },
    data_type=DataClassification.CURRENT_POSITION.value,
    purpose="emergency:fire",
    bypass_consent=True  # ⚠️ EMERGENCY ONLY
)

# Automatically logged with EMERGENCY_BYPASS flag
```

## API Reference

See full API documentation in `backend/privacy/docs/api.md`

## Contributing

This is proprietary software. For internal development only.

## Support

- **Privacy Team**: privacy@ada.sea
- **Data Protection Officer**: dpo@ada.sea
- **Security Issues**: security@ada.sea

---

**"Kaptan ne derse o olur. Nokta."**
