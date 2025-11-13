# Ada Maritime AI - Demo Guide

Complete demonstration guide for showcasing the system.

---

## Demo Overview

**Duration**: 30 minutes
**Audience**: Marina managers, port authorities, maritime safety officers
**Goal**: Showcase VERIFY Agent compliance system and VHF monitoring capabilities

---

## Demo Setup

### 1. Prerequisites

```bash
# Start all services
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Load demo data
python scripts/load_demo_data.py
```

### 2. Demo Data

**Test Marinas**:
- Marina Demo (marina_demo_001)
- Test vessels with various compliance states

**Demo Scenarios**:
1. Vessel with expired insurance
2. Hot work permit workflow
3. Compliance violation detection
4. VHF intership communication
5. Daily audit report

---

## Demo Script

### Part 1: System Introduction (5 minutes)

**Opening Statement**:

> "Ada Maritime AI is an AI-powered compliance and monitoring system designed for Turkish marinas. It automates the enforcement of all 176 articles from the West Istanbul Marina Operation Regulations and provides real-time VHF communication monitoring."

**Key Features to Highlight**:
- ✅ Automated compliance checking
- 🛡️ Insurance verification (Article E.2.1)
- 🔥 Hot work permit management (Article E.5.5)
- 📡 VHF ship-to-ship monitoring
- 📊 Real-time dashboard and reporting

---

### Part 2: Vessel Entry Verification (5 minutes)

**Scenario**: Vessel "Sea Dream" requests marina entry

#### Step 1: Show Vessel Verification Request

```bash
# API Demo
curl -X POST http://localhost:8000/api/v1/verify/vessel \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_name": "Sea Dream",
    "vessel_registration": "TR-123456",
    "marina_id": "marina_demo_001"
  }'
```

**Expected Response**:
```json
{
  "entry_authorized": false,
  "violations": [
    {
      "article": "E.2.1",
      "severity": "critical",
      "description": "Insurance expired 15 days ago"
    }
  ],
  "required_actions": [
    "Renew third-party liability insurance",
    "Submit proof to marina office"
  ]
}
```

**Talking Points**:
- System automatically checks Article E.2.1 insurance requirements
- Critical violations prevent marina entry
- Clear actions provided to vessel owner

#### Step 2: Show Dashboard View

Open browser to: `http://localhost:3000/compliance`

**Highlight**:
- Vessel list with compliance status
- Red warning for "Sea Dream"
- Insurance expiry dates
- Violation severity indicators

---

### Part 3: Hot Work Permit Workflow (7 minutes)

**Scenario**: Welding repairs needed on "Ocean Star" yacht

#### Step 1: Request Hot Work Permit

```bash
curl -X POST http://localhost:8000/api/v1/verify/permit/request \
  -H "Content-Type: application/json" \
  -d '{
    "work_description": "Welding repairs on hull",
    "work_location": "Berth A12",
    "scheduled_start": "2025-11-13T10:00:00",
    "scheduled_end": "2025-11-13T16:00:00",
    "requested_by": "Captain Smith",
    "requester_email": "smith@oceanstar.com",
    "requester_phone": "+90 555 1234567",
    "marina_id": "marina_demo_001"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "permit_id": "permit_20251113_001",
  "status": "pending_approval",
  "fire_watch_required": true,
  "safety_equipment_required": [
    "fire_extinguisher",
    "fire_blanket",
    "safety_goggles",
    "protective_gloves"
  ],
  "notification_sent": true
}
```

**Talking Points**:
- Article E.5.5 hot work safety requirements enforced
- Fire watch automatically required for welding
- Marina manager receives email notification
- Safety equipment checklist provided

#### Step 2: Show Approval Process

Open: `http://localhost:3000/permits/permit_20251113_001`

**Demonstrate**:
- Permit details and safety requirements
- Approve permit (as marina manager)
- Email notification to requester
- Permit appears in active permits list

#### Step 3: Show Real-time Monitoring

Open: `http://localhost:3000/permits/active`

**Highlight**:
- Active permits with countdown timers
- Fire watch status indicator
- Safety compliance checklist
- Automatic violation detection if requirements not met

---

### Part 4: VHF Communication Monitoring (7 minutes)

**Scenario**: Monitor intership communications

#### Step 1: Show VHF Dashboard

Open: `http://localhost:3000/vhf-monitor`

**Highlight**:
- Real-time channel monitoring (CH 16, 6, 72, 73)
- Channel activity indicators
- Priority channels (emergency CH 16)
- Turkey marina VHF database (18 marinas)

#### Step 2: Show Intership Communication

**Demonstrate**:
- Channel 73 communication detected
- Signal strength meter
- Vessel identification
- Audio recording capability
- Speech-to-text transcription

**Example Communication Log**:
```
[13:45:30] CH 73 (156.675 MHz)
Vessel: "Ocean Star to Marina Dream"
Signal: -62 dBm (Strong)
Transcription: "Approaching Ataköy Marina, requesting berth assignment..."
```

#### Step 3: Show Marina VHF Configuration

Open: `http://localhost:3000/vhf-monitor/config`

**Show Turkey Marina Database**:
- Ataköy Marina: CH 73 primary, CH 6/72/73 intership
- West Istanbul Marina: CH 72 primary
- Bodrum: CH 73
- Marmaris: CH 72
- All 18 Turkish marinas configured

**Talking Points**:
- Complete Turkey marina VHF coverage
- Automatic channel switching based on marina
- Priority monitoring of emergency channels
- Integration with Ada Observer for AI analysis

---

### Part 5: Compliance Dashboard (4 minutes)

#### Step 1: Show Marina Dashboard

Open: `http://localhost:3000/dashboard`

**Highlight**:
- Total active violations by severity
- Insurance expiry alerts
- Active hot work permits
- Recent compliance activity

**Example Dashboard**:
```
📊 Marina Demo - Compliance Overview

⚠️ Active Violations
  Critical: 2
  High: 5
  Medium: 12
  Low: 8

🛡️ Insurance Status
  Valid: 85 vessels
  Expiring Soon (30 days): 12
  Expired: 3

🔥 Hot Work Permits
  Active: 2
  Pending Approval: 1
  Completed Today: 5
```

#### Step 2: Run Live Audit

```bash
curl -X POST http://localhost:8000/api/v1/verify/audit \
  -H "Content-Type: application/json" \
  -d '{
    "marina_id": "marina_demo_001",
    "include_recommendations": true
  }'
```

**Show Results**:
- Article-by-article compliance check
- Violation summary
- Recommendations for resolution
- Response time requirements

---

### Part 6: Email Notifications (2 minutes)

**Show Email Templates**:

#### Violation Alert Email
- Critical severity highlighted
- Article reference
- Required actions listed
- Response time deadline
- Link to resolve

#### Insurance Expiry Warning
- Vessel details
- Days until expiry
- Article E.2.1 reference
- Renewal instructions

#### Permit Approval Email
- Permit details
- Safety requirements checklist
- Fire watch reminder
- Work schedule

**Talking Points**:
- Automated email notifications
- Marina managers stay informed
- Vessel owners receive timely reminders
- Compliance deadlines enforced

---

## Demo Q&A Preparation

### Common Questions

**Q: How many articles does it check?**
A: All 176 articles from West Istanbul Marina Operation Regulations. We've implemented the 24 most critical articles with full automation.

**Q: What happens if a vessel violates regulations?**
A: Violations are logged with severity levels (Critical/High/Medium/Low). Critical violations (like expired insurance) prevent marina entry. Response times are enforced based on severity.

**Q: Can it integrate with our existing marina software?**
A: Yes, via REST API. We provide complete API documentation and can integrate with booking systems, berth management, billing, etc.

**Q: What VHF channels are monitored?**
A: Priority channels: 16 (emergency), 72, 73 (intership). We monitor all marina-specific channels plus ship-to-ship communications.

**Q: How accurate is the VHF transcription?**
A: We use OpenAI Whisper for speech-to-text with 85-95% accuracy for clear VHF transmissions. AI filters out false positives.

**Q: What about data privacy?**
A: All data is encrypted at rest and in transit. JWT authentication for all API access. GDPR compliant. Vessel data stored securely with access controls.

**Q: How much does it cost?**
A: Contact us for pricing. Based on marina size (berth count), features needed, and API usage.

---

## Demo Tips

### Do's:
✅ Practice demo flow beforehand
✅ Have backup data ready
✅ Show both success and failure scenarios
✅ Emphasize automation and time savings
✅ Highlight compliance with Turkish regulations
✅ Demonstrate mobile responsiveness

### Don'ts:
❌ Skip error scenarios
❌ Overwhelm with technical details
❌ Rush through permit workflow
❌ Forget to show email notifications
❌ Ignore questions about integration

---

## Demo Variations

### Quick Demo (15 minutes)
1. System introduction (2 min)
2. Vessel verification failure (3 min)
3. Hot work permit request (5 min)
4. VHF monitoring (3 min)
5. Dashboard overview (2 min)

### Technical Deep Dive (60 minutes)
- Include API endpoint details
- Show database schema
- Demonstrate AI agent reasoning
- Explain compliance rule engine
- Review SDR configuration

### Executive Summary (10 minutes)
- Focus on ROI and time savings
- Show compliance statistics
- Highlight automation benefits
- Emphasize safety improvements

---

## Demo Assets

### Required Files
- `scripts/load_demo_data.py` - Loads demo vessels and scenarios
- `docs/presentation.pdf` - Slide deck
- `docs/screenshots/` - Dashboard screenshots
- `docs/videos/` - Screen recordings

### Demo Credentials
```
Admin Account:
Email: demo@adamaritime.ai
Password: DemoAdmin123!

Marina Manager:
Email: manager@demo-marina.com
Password: Manager123!
```

---

## Post-Demo Follow-up

**Materials to Share**:
- [ ] Demo recording video
- [ ] Presentation slides
- [ ] Technical documentation
- [ ] API documentation
- [ ] Pricing sheet
- [ ] Case studies
- [ ] Trial access credentials

**Next Steps**:
1. Schedule follow-up meeting
2. Provide trial access
3. Gather requirements
4. Prepare custom demo for their marina
5. Integration planning session

---

## Success Metrics

Track demo effectiveness:
- Audience engagement
- Questions asked
- Feature requests
- Follow-up meetings scheduled
- Trials activated
- Deals closed

---

**Demo Version**: 1.0
**Last Updated**: 2025-11-13
**Contact**: demo@adamaritime.ai
