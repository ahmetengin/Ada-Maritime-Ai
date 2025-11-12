# 🔒 ADA.SEA PRIVACY-FIRST ARCHITECTURE

## Privacy Manifesto: "Kaptan ne derse o olur. Nokta."

Ada.Sea is built on a **zero-trust, privacy-first architecture** where the captain has complete control over all data. No automatic cloud sync, no third-party sharing, and explicit approval required for every single data transfer.

---

## Core Privacy Principles

### 1. **Zero Trust by Default**
- NO automatic data sharing
- NO cloud synchronization by default
- NO third-party integrations without approval
- Everything starts as DENIED

### 2. **Explicit Consent**
- Captain voice approval required for ALL data transfers
- Clear explanation of what, where, and why
- Per-transfer or standing permission options
- Revocable at any time

### 3. **Minimal Data**
- Only share what's absolutely necessary
- Data minimization for every purpose
- Automatic filtering of unnecessary fields
- Anonymous aggregation when possible

### 4. **Complete Transparency**
- Full audit trail of all data transfers
- Tamper-proof logging
- Real-time notifications to captain
- Easy-to-review transfer history

### 5. **Captain Control**
- Right to access all data
- Right to rectify incorrect data
- Right to delete (be forgotten)
- Right to restrict processing
- Right to data portability
- Right to object

### 6. **Edge Computing**
- All processing on Mac Mini M4 (on vessel)
- Local encrypted storage
- No required internet connectivity
- Cloud optional, never mandatory

### 7. **Zero-Knowledge Cloud** (Optional)
- Client-side encryption only
- Ada.Sea cannot read backups
- Captain holds encryption keys
- Instant deletion available

### 8. **Regulation Ready**
- KVKK (Turkish Data Protection Law) compliant
- GDPR (EU) compliant
- Privacy by Design
- Privacy by Default

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│               ADA.SEA PRIVACY CORE                  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │          AdaSeaPrivacyCore                  │  │
│  │  - Zero Trust Mode: ON                      │  │
│  │  - Captain Auth Required: YES               │  │
│  │  - Cloud Sync: DISABLED                     │  │
│  └─────────────────────────────────────────────┘  │
│                       │                            │
│         ┌─────────────┼─────────────┐             │
│         │             │             │             │
│    ┌────▼───┐   ┌────▼────┐   ┌───▼────┐        │
│    │ Data   │   │ Consent │   │ Audit  │        │
│    │ Policy │   │ Manager │   │  Log   │        │
│    └────────┘   └─────────┘   └────────┘        │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │        Data Classification                   │  │
│  │  PRIVATE     → Never share                  │  │
│  │  RESTRICTED  → Essential only, with approval│  │
│  │  CONDITIONAL → Captain consent required     │  │
│  │  ANONYMOUS   → No identification            │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │        Compliance Framework                  │  │
│  │  • KVKK (Turkish Law 6698)                  │  │
│  │  • GDPR (EU Regulation 2016/679)            │  │
│  │  • Privacy by Design/Default                │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Implementation

### Python Backend (`backend/privacy/`)

```
privacy/
├── __init__.py                  # Module initialization
├── privacy_core.py              # Core privacy management
├── data_policy.py               # Data classification & permissions
├── consent_manager.py           # Captain consent handling
├── audit_log.py                 # Audit trail & transparency
├── marina_integration.py        # Ada.Marina integration
└── compliance.py                # KVKK & GDPR compliance
```

### Key Components

#### 1. Privacy Core (`privacy_core.py`)
Main orchestration of privacy controls:

```python
from backend.privacy import AdaSeaPrivacyCore

# Initialize privacy core
privacy = AdaSeaPrivacyCore(
    captain_id="boss@ada.sea",
    data_policy=None,  # Uses default secure policy
    audit_log_path=None  # Uses default encrypted storage
)

# Attempt to share data (requires captain approval)
result = await privacy.share_data(
    destination="Yalikavak Marina",
    data={'vessel_length': 65, 'arrival_time': '2025-11-13T14:00:00Z'},
    data_type="vessel_specifications",
    purpose="berth_reservation"
)

# Returns consent request for captain approval
if not result['success'] and 'voice_prompt' in result:
    print(result['voice_prompt'])
    # "Kaptan, Yalikavak Marina için vessel_specifications
    #  verisi paylaşılsın mı? Amaç: berth_reservation.
    #  Cevap: 'Evet paylaş' veya 'Hayır'"
```

#### 2. Data Policy (`data_policy.py`)
Granular data classification:

```python
from backend.privacy import DataPolicy, DataClassification, PermissionLevel

policy = DataPolicy()

# Check if data type can be shared
if policy.is_private_data(DataClassification.GPS_HISTORY):
    print("NEVER share GPS history")

# Get minimal data for purpose
minimal = policy.get_minimal_data_for_purpose('berth_reservation')
# Returns: [VESSEL_SPECIFICATIONS, ARRIVAL_TIME]
# NOT: GPS_HISTORY, FINANCIAL_DATA, etc.
```

#### 3. Consent Manager (`consent_manager.py`)
Handle captain approvals:

```python
from backend.privacy import ConsentManager, ConsentMethod

manager = ConsentManager()

# Create consent request
request = await manager.request_captain_permission(
    destination="Ada.marina:Yalikavak",
    data_type="vessel_specifications",
    data_size=256,
    purpose="berth_assignment"
)

# Process captain's response
consent = await manager.process_captain_response(
    request_id=request.request_id,
    granted=True,
    captain_id="boss@ada.sea",
    method=ConsentMethod.VOICE,
    confirmation_text="Evet paylaş"
)

# Set up standing permission
consent = await manager.process_captain_response(
    request_id=request.request_id,
    granted=True,
    captain_id="boss@ada.sea",
    method=ConsentMethod.VOICE,
    standing=True,
    expiry_hours=168  # 7 days
)
```

#### 4. Audit Log (`audit_log.py`)
Complete transparency:

```python
from backend.privacy import AuditLog

audit = AuditLog()

# Log data transfer
entry = audit.log_transfer(
    destination="Yalikavak Marina",
    data_type="vessel_specifications",
    captain_id="boss@ada.sea",
    authorization_method="voice_confirmed",
    result="success",
    data={'vessel_length': 65},
    confirmation_text="Evet paylaş"
)

# Query audit trail
entries = audit.query(
    captain_id="boss@ada.sea",
    hours=168  # Last 7 days
)

# Get summary for captain
summary = audit.get_summary("boss@ada.sea", hours=168)
print(f"Total transfers: {summary['total_transfers']}")

# Export for captain review
report = audit.export_for_captain(
    captain_id="boss@ada.sea",
    hours=168,
    format="human"  # or "json"
)
```

#### 5. Ada.Marina Integration (`marina_integration.py`)
Trust boundary enforcement:

```python
from backend.privacy import AdaMarinaIntegration

integration = AdaMarinaIntegration(privacy_core)

# Request berth assignment (requires approval)
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

# Set up standing permission
result = integration.setup_standing_permission(
    marina_id="yalikavak",
    permission_type="vessel_specs",
    expiry_hours=168
)
```

#### 6. Compliance (`compliance.py`)
KVKK and GDPR:

```python
from backend.privacy import KVKKCompliance, GDPRCompliance

# KVKK (Turkish Law)
kvkk = KVKKCompliance()

# Handle data subject request
result = kvkk.handle_data_subject_request(
    request_type='bilgi_talep',  # Access request
    captain_id='boss@ada.sea'
)

# Generate privacy notice
notice = kvkk.framework.generate_privacy_notice(language='tr')

# GDPR (EU)
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

---

## Voice Commands

### Data Sharing Control

**Turkish:**
```
"Ada, veri paylaşım geçmişini göster"
"Ada, hangi bilgileri kimle paylaştım?"
"Ada, Yalikavak Marina'ya ne gönderdin?"
"Ada, tüm otomatik paylaşımları iptal et"
"Ada, marina izinlerini göster"
```

**English:**
```
"Ada, show data sharing history"
"Ada, what information did I share with whom?"
"Ada, what did you send to Yalikavak Marina?"
"Ada, cancel all automatic sharing"
"Ada, show marina permissions"
```

### KVKK/GDPR Rights

**Turkish:**
```
"Ada, verilerimi göster"           # Right to access
"Ada, [veri]'yi düzelt"            # Right to rectification
"Ada, [veri]'yi sil"               # Right to erasure
"Ada, [veri] paylaşımını durdur"   # Right to restriction
"Ada, verilerimi dışa aktar"       # Right to portability
"Ada, [işleme] itiraz ediyorum"    # Right to object
```

### Marina Integration

**Turkish:**
```
"Ada, marina'ya check-in yap"
"Ada, Yalikavak Marina'da berth reserve et"
"Ada, marina'ya yakıt talep et"
"Ada, West Istanbul Marina için otomatik paylaşımı aktif et"
```

---

## Data Flow Example

### Scenario: Marina Berth Reservation

```
1. Captain Request:
   "Ada, Yalikavak Marina'da berth reserve et"

2. Privacy Core Processing:
   ├─ Data Policy Check
   │  └─ vessel_specifications: RESTRICTED
   │     (Requires approval, but not PRIVATE)
   │
   ├─ Standing Permission Check
   │  └─ None found for Yalikavak Marina
   │
   └─ Create Consent Request
      ├─ Destination: Ada.marina:Yalikavak
      ├─ Data: vessel_length, vessel_beam, vessel_draft, arrival_time
      ├─ Purpose: berth_reservation
      └─ Size: 256 bytes

3. Captain Approval Prompt:
   "Kaptan, Yalikavak Marina'ya rezervasyon için
    şu bilgileri göndermem gerekiyor:
    - Tekne uzunluğu: 65 feet
    - Tekne genişliği: 18 feet
    - Tekne drafı: 3 meters
    - Varış tarihi: Yarın saat 14:00

    Onaylıyor musunuz?"

4. Captain Response:
   "Evet, paylaş"

5. Data Transfer:
   ├─ Filter data by consent scope
   ├─ Execute transfer to Ada.marina:Yalikavak
   ├─ Log in audit trail
   │  ├─ Timestamp: 2025-11-12T14:32:00Z
   │  ├─ Destination: Ada.marina:Yalikavak
   │  ├─ Data: vessel_specifications
   │  ├─ Captain: boss@ada.sea
   │  ├─ Authorization: voice_confirmed
   │  └─ Data Hash: a3f2c8...
   └─ Notify Captain: "✅ Rezervasyon talebi gönderildi"

6. Audit Entry Created:
   [2025-11-12 14:32:00] Veri Gönderildi
     Hedef: Ada.marina:Yalikavak
     Veri: vessel_specifications
     Yetki: voice_confirmed
     Sonuç: success
```

### What Was NOT Sent:
- ❌ GPS history
- ❌ Current position
- ❌ Financial data
- ❌ Crew information
- ❌ Communication logs
- ❌ Sensor data
- ❌ Security camera footage

---

## Comparison with Other Systems

| Feature | Zora | Garmin | Raymarine | **Ada.Sea** |
|---------|------|--------|-----------|-------------|
| **Default Cloud Sync** | ✓ Yes | ✓ Yes | ✓ Yes | **✗ No** |
| **Third-party Sharing** | Via SDK | Limited | Limited | **Captain Only** |
| **Encryption** | TLS | TLS | TLS | **E2E + At-rest** |
| **Data Ownership** | Unclear | Vendor | Vendor | **100% Captain** |
| **Audit Trail** | Limited | No | No | **Complete** |
| **Right to Delete** | Support | Support | Support | **Instant** |
| **Anonymous Mode** | No | No | No | **Yes** |
| **KVKK Compliant** | ? | No | No | **✓ Yes** |
| **GDPR Compliant** | ? | Partial | Partial | **✓ Yes** |
| **On-device AI** | No | No | No | **✓ Yes** |
| **Zero-Knowledge Backup** | No | No | No | **✓ Yes** |
| **Voice Privacy Control** | No | No | No | **✓ Yes** |

---

## Demo Scenario: West Istanbul Marina

### Captain Commands
```
Kaptan: "Ada, West Istanbul Marina'ya check-in yap"

Ada.sea: "Marina'ya şu bilgileri göndermem gerekiyor:
         - Tekne: Phisedelia
         - Uzunluk: 65 feet
         - Berth: C-42

         Onaylıyor musunuz?"

Kaptan: "Evet"

Ada.sea: ✓ "Check-in tamamlandı.
         Marina hoş geldiniz mesajı gönderdi."
```

### Internal Logging
```json
{
  "timestamp": "2025-11-12T15:45:00Z",
  "event_type": "data_transfer",
  "destination": "Ada.marina:WestIstanbul",
  "data_sent": {
    "vessel_name": "Phisedelia",
    "vessel_length": 65,
    "berth_number": "C-42"
  },
  "data_not_sent": [
    "gps_history",
    "crew_info",
    "financial_data",
    "communication_logs"
  ],
  "captain_authorization": {
    "method": "voice_confirmation",
    "captain_id": "boss@ada.sea",
    "confirmation_text": "Evet"
  },
  "result": "success"
}
```

---

## Security Architecture

### Defense in Depth

```
LAYER 1: Physical Security
├─ Mac Mini M4 on-board (captain's control)
├─ No remote admin access
└─ Tamper-evident seals

LAYER 2: Network Security
├─ VPN for outbound (if enabled)
├─ Firewall: deny all inbound
├─ mTLS for marina connections
└─ Certificate pinning

LAYER 3: Application Security
├─ Sandboxed processes
├─ Encrypted local storage
├─ Memory encryption
└─ Code signing

LAYER 4: Data Security
├─ AES-256-GCM encryption
├─ Zero-knowledge backup
├─ Secure key management
└─ Data integrity hashing

LAYER 5: Access Control
├─ Captain biometric auth
├─ Voice signature verification
├─ Session timeouts
└─ Multi-factor for sensitive ops

LAYER 6: Audit & Compliance
├─ Complete activity log
├─ Tamper-proof audit trail
├─ Regular security reviews
└─ Compliance monitoring
```

---

## Future Enhancements

### Phase 1 (Complete) ✅
- [x] Privacy core architecture
- [x] Data classification system
- [x] Consent management
- [x] Audit logging
- [x] KVKK/GDPR compliance
- [x] Ada.Marina integration

### Phase 2 (Q1 2026)
- [ ] Voice signature verification
- [ ] Biometric authentication
- [ ] Zero-knowledge cloud backup
- [ ] Encrypted peer-to-peer sharing
- [ ] Privacy dashboard UI

### Phase 3 (Q2 2026)
- [ ] Advanced anonymization
- [ ] Differential privacy
- [ ] Homomorphic encryption
- [ ] Decentralized identity (DID)
- [ ] Blockchain audit trail

### Phase 4 (Q3 2026)
- [ ] Multi-language support
- [ ] Compliance automation
- [ ] Privacy score dashboard
- [ ] Third-party privacy audits
- [ ] ISO 27001 certification

---

## Testing & Validation

### Unit Tests
```bash
cd backend
python -m pytest privacy/tests/
```

### Integration Tests
```bash
python -m pytest tests/integration/test_privacy_flow.py
```

### Compliance Validation
```bash
python -m privacy.compliance validate --framework=kvkk
python -m privacy.compliance validate --framework=gdpr
```

---

## Documentation

- **User Manual**: [USERMANUAL.md](USERMANUAL.md)
- **API Documentation**: `backend/privacy/docs/`
- **Compliance Guide**: `backend/privacy/docs/compliance.md`
- **Integration Guide**: [docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md)

---

## Support

For privacy-related questions or concerns:

- **Privacy Team**: privacy@ada.sea
- **Data Protection Officer**: dpo@ada.sea
- **KVKK Requests**: kvkk@ada.sea
- **Security Issues**: security@ada.sea

---

## License

Ada.Sea Privacy Architecture is proprietary software.
Copyright © 2025 Ada.Sea Platform

---

**"Kaptan ne derse o olur. Nokta."**

*Your vessel. Your data. Your control.*
