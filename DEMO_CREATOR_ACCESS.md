# 🎬 DEMO: Creator Access in Action

## Scenario: Debugging GPS Module

### Characters
- **Creator (Sen)**: System developer
- **Captain**: Vessel owner (Phisedelia)
- **Ada**: AI assistant

---

## Act 1: Creator Needs Access

```python
from backend.privacy import CreatorAccessManager, AccessReason

# Initialize
manager = CreatorAccessManager(captain_id="boss@ada.sea")

# Creator requests access
result = manager.request_creator_access(
    creator_id="ahmet@ada.sea",
    reason=AccessReason.DEBUGGING,
    justification="GPS coordinates not updating correctly",
    duration_hours=4,  # Short duration for bug fix
    scope=['gps_module', 'navigation_system', 'sensor_logs']
)
```

**Output:**
```
✅ Creator access granted
⚠️  Captain has been notified
⚠️  Token expires in 4 hours
⚠️  All actions will be logged

Token ID: 3a7f2c9d4e8b1f6a
```

---

## Act 2: Captain Receives Notification

**Captain's Screen:**
```
╔═══════════════════════════════════════════════════════════╗
║  📢 CREATOR ACCESS NOTIFICATION                           ║
╟───────────────────────────────────────────────────────────╢
║  Creator: ahmet@ada.sea                                   ║
║  Reason: Debugging                                        ║
║  Problem: GPS coordinates not updating correctly          ║
║                                                           ║
║  Will Access:                                             ║
║  • GPS module                                             ║
║  • Navigation system                                      ║
║  • Sensor logs                                            ║
║                                                           ║
║  Duration: 4 hours                                        ║
║  Started: 2025-11-12 14:30:00                             ║
║  Expires: 2025-11-12 18:30:00                             ║
║                                                           ║
║  ⚠️  All creator actions will be logged.                   ║
║  ⚠️  You can see everything the creator does.             ║
║  ⚠️  You can revoke access anytime.                        ║
║                                                           ║
║  Voice: "Ada, creator ne yaptı?" to see activity          ║
╚═══════════════════════════════════════════════════════════╝
```

**Captain's Reaction:**
```
Captain: "Ada, tamam, anladım"
Ada: "✓ Bilgilendirme alındı. Creator'ın tüm aksiyonlarını
      görebileceksiniz."
```

---

## Act 3: Creator Works (All Actions Logged)

```python
# Creator reads GPS data
result = manager.creator_access_data(
    token_id="3a7f2c9d4e8b1f6a",
    data_type="gps_history",
    data=gps_data,
    action="read"
)
```

**Logged:**
```
[2025-11-12 14:31:15] Creator Data Access
  Action: read
  Data Type: gps_history
  Data Hash: a3f2c84b7e1d...
  Creator: ahmet@ada.sea
  Token: 3a7f2c9d4e8b1f6a
  Captain Notified: Yes
```

```python
# Creator reads sensor logs
result = manager.creator_access_data(
    token_id="3a7f2c9d4e8b1f6a",
    data_type="sensor_logs",
    data=sensor_logs,
    action="read"
)
```

**Logged:**
```
[2025-11-12 14:32:40] Creator Data Access
  Action: read
  Data Type: sensor_logs
  Data Hash: b7e1d4c9f2a8...
  Creator: ahmet@ada.sea
```

```python
# Creator modifies code
result = manager.creator_access_data(
    token_id="3a7f2c9d4e8b1f6a",
    data_type="source_code",
    data="gps_tracking.py lines 142-156",
    action="modify"
)
```

**Logged:**
```
[2025-11-12 14:35:20] Creator Code Modification
  Action: modify
  Module: gps_tracking.py
  Lines: 142-156
  Creator: ahmet@ada.sea
  Change Hash: c9f2a8d3b5e7...
```

---

## Act 4: Captain Checks Activity (30 Minutes Later)

**Captain to Ada:**
```
Captain: "Ada, creator ne yaptı?"

Ada: "Creator son 30 dakikada şunları yaptı:

      [14:31:15] GPS geçmişi verilerini okudu
      [14:32:40] Sensör loglarını okudu
      [14:35:20] gps_tracking.py dosyasını düzenledi

      Toplam 3 aksiyon.
      Daha fazla detay ister misiniz?"

Captain: "Evet, detay göster"

Ada: "Detaylı rapor:

     ╔═══════════════════════════════════════════════╗
     ║  CREATOR ACCESS LOG (Detailed)               ║
     ╟───────────────────────────────────────────────╢
     ║                                               ║
     ║  [14:31:15] GPS History Read                 ║
     ║    • 2,450 GPS coordinates                   ║
     ║    • Last 7 days                             ║
     ║    • Data hash: a3f2c84b...                  ║
     ║                                               ║
     ║  [14:32:40] Sensor Logs Read                 ║
     ║    • Engine sensors                          ║
     ║    • Navigation sensors                      ║
     ║    • Data hash: b7e1d4c9...                  ║
     ║                                               ║
     ║  [14:35:20] Code Modified                    ║
     ║    • File: gps_tracking.py                   ║
     ║    • Lines changed: 142-156                  ║
     ║    • Purpose: Fix coordinate update logic    ║
     ║    • Change hash: c9f2a8d3...                ║
     ║                                               ║
     ║  Status: Creator still has access            ║
     ║  Expires: 18:30:00 (3.5 hours remaining)     ║
     ║                                               ║
     ║  Voice: 'Ada, creator access'i iptal et'     ║
     ║         to revoke access                     ║
     ╚═══════════════════════════════════════════════╝"
```

---

## Act 5: Sensitive Operation Requires Approval

2 hours later, creator needs financial data for testing payment flow:

```python
result = manager.request_creator_access(
    creator_id="ahmet@ada.sea",
    reason=AccessReason.DEBUGGING,
    justification="Need to test marina payment integration",
    duration_hours=2,
    scope=['financial_data', 'payment_logs'],
    sensitive=True  # ⚠️ Requires captain approval
)
```

**Captain Notification:**
```
╔═══════════════════════════════════════════════════════════╗
║  🔴 SENSITIVE ACCESS REQUEST - APPROVAL REQUIRED          ║
╟───────────────────────────────────────────────────────────╢
║  Creator: ahmet@ada.sea                                   ║
║  Reason: Debugging                                        ║
║  Problem: Testing marina payment integration             ║
║                                                           ║
║  ⚠️  WANTS TO ACCESS SENSITIVE DATA:                       ║
║  • Financial transaction data                             ║
║  • Payment logs                                           ║
║                                                           ║
║  Duration: 2 hours                                        ║
║                                                           ║
║  ⚠️  This requires YOUR APPROVAL                           ║
║                                                           ║
║  Voice Commands:                                          ║
║  • "Ada, creator access'i onayla"                         ║
║  • "Ada, creator access'i reddet"                         ║
╚═══════════════════════════════════════════════════════════╝
```

**Captain's Decision:**
```
Captain: "Ada, neden mali verilere erişmek istiyor?"

Ada: "Creator, marina ödeme entegrasyonunu test etmek istiyor.
      Yalikavak Marina ile otomatik ödeme sistemini debug ediyor."

Captain: "Tamam, anladım. Onayla."

Ada: "✓ Creator access onaylandı.
      Mali verilere 2 saat boyunca erişebilir.
      Tüm aksiyonlar loglanacak."
```

```python
# Captain approves
result = manager.captain_approve_creator_access(
    token_id="4b8c3d2e1f9a...",
    approved=True,
    captain_note="Payment integration testing approved"
)
```

---

## Act 6: Captain Decides to Revoke Early

1 hour later, captain wants to revoke access:

```
Captain: "Ada, creator access'i iptal et"

Ada: "Hangi access'i iptal etmek istersiniz?

     Aktif creator access'ler:
     1. GPS debugging (ahmet@ada.sea) - 2.5 saat kaldı
     2. Payment testing (ahmet@ada.sea) - 1 saat kaldı

     Hepsini mi yoksa birini mi?"

Captain: "Hepsini iptal et"

Ada: "✓ 2 creator access token'ı iptal edildi.
     ✓ Creator artık sisteme erişemiyor.
     ✓ İptal log'a kaydedildi."
```

```python
# System revokes all access
result = manager.captain_revoke_creator_access()
# Output: {'success': True, 'message': 'Revoked 2 tokens', 'count': 2}
```

**Creator Side:**
```python
# Creator tries to access
result = manager.validate_creator_access(
    token_id="3a7f2c9d4e8b1f6a",
    action="read_data"
)

# Output: {'valid': False, 'reason': 'Token revoked by captain'}
```

---

## Act 7: Captain Reviews Complete Log

End of day, captain wants full report:

```
Captain: "Ada, bugün creator'ın tüm aktivitelerini göster"

Ada: "Bugün creator toplam 2 access talebi yaptı:

     ╔═══════════════════════════════════════════════════════╗
     ║  DAILY CREATOR ACCESS REPORT                         ║
     ║  Date: 2025-11-12                                    ║
     ╟───────────────────────────────────────────────────────╢
     ║                                                       ║
     ║  ACCESS REQUEST #1                                    ║
     ║  ─────────────────────────────────────────────────── ║
     ║  Time: 14:30:00 - 16:45:00 (revoked early)          ║
     ║  Reason: GPS debugging                                ║
     ║  Status: Approved, then revoked                       ║
     ║                                                       ║
     ║  Actions Performed:                                   ║
     ║  • [14:31:15] Read GPS history (2,450 coordinates)   ║
     ║  • [14:32:40] Read sensor logs                       ║
     ║  • [14:35:20] Modified gps_tracking.py (14 lines)    ║
     ║  • [14:42:10] Tested GPS fix                         ║
     ║  • [15:10:30] Read navigation logs                   ║
     ║  • [15:25:45] Modified navigation.py (8 lines)       ║
     ║  • [16:45:00] ACCESS REVOKED BY CAPTAIN              ║
     ║                                                       ║
     ║  Total Actions: 7                                     ║
     ║                                                       ║
     ║  ─────────────────────────────────────────────────── ║
     ║                                                       ║
     ║  ACCESS REQUEST #2                                    ║
     ║  ─────────────────────────────────────────────────── ║
     ║  Time: 16:30:00 - 16:45:00 (revoked early)          ║
     ║  Reason: Payment integration testing                  ║
     ║  Status: Required approval → Approved → Revoked      ║
     ║                                                       ║
     ║  Actions Performed:                                   ║
     ║  • [16:32:15] Read payment logs                      ║
     ║  • [16:35:00] Read financial transaction data        ║
     ║  • [16:45:00] ACCESS REVOKED BY CAPTAIN              ║
     ║                                                       ║
     ║  Total Actions: 3                                     ║
     ║                                                       ║
     ║  ═══════════════════════════════════════════════════ ║
     ║                                                       ║
     ║  SUMMARY                                              ║
     ║  • Total Access Requests: 2                          ║
     ║  • Total Actions: 10                                 ║
     ║  • Data Read: GPS, sensors, logs, payments           ║
     ║  • Code Modified: 2 files (22 lines)                 ║
     ║  • Sensitive Data: Payment logs (with approval)      ║
     ║  • Both access revoked by captain                    ║
     ║                                                       ║
     ║  ✓ All actions logged                                ║
     ║  ✓ No unauthorized access                            ║
     ║  ✓ Captain maintained control                        ║
     ║                                                       ║
     ╚═══════════════════════════════════════════════════════╝"
```

---

## Key Takeaways

### ✅ Creator CAN:
- Access everything for development
- Debug production issues
- Modify code
- Read all data

### ✅ Captain CAN:
- See everything creator does
- Approve/deny sensitive operations
- Revoke access anytime
- Review complete logs

### ✅ System GUARANTEES:
- All creator actions logged
- Captain always notified
- Sensitive data requires approval
- Complete transparency

---

## The Balance

```
Creator: "Her şeye ulaşırım"          → TRUE ✅
Captain: "Ne yaptığını görürüm"       → TRUE ✅
System: "İkisi de kontroldedir"       → TRUE ✅
```

**No Contradiction. Perfect Harmony.**

---

*This is the Ada.Sea way: Trust through Transparency, Not Obstruction.*
