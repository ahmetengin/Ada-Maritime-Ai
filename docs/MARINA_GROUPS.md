# Marina Groups Integration

## Overview

Ada Maritime AI now supports **multi-group marina operations** with comprehensive coverage of Turkey's two largest premium marina operators.

**Total Coverage:** 12 marinas | ~4,867 berths

---

## 📊 Marina Groups

### 1. **Setur Marinas** (Turkey's Leading Marina Chain)

| Marina | Location | Berths | Region | Special Features |
|--------|----------|--------|--------|-----------------|
| **Netsel Setur Marmaris** | Marmaris, Muğla | 830 | Aegean | Largest in network, superyacht hub |
| **Setur Kuşadası** | Kuşadası, Aydın | 580 | Aegean | Pool, spa, shopping center |
| **Setur Kaş** | Kaş, Antalya | 472 | Mediterranean | 160 dry storage, mega yacht capable |
| **Setur Bodrum** | Bodrum, Muğla | 450 | Aegean | Premier location, full services |
| **Setur Çeşme** | Çeşme, İzmir | 380 | Aegean | Sailing school, wind sports |
| **Setur Finike** | Finike, Antalya | 320 | Mediterranean | Gateway to Lycian coast |
| **Setur Yalova** | Yalova | 240 | Marmara | Only marina on Sea of Marmara (non-Istanbul) |
| **Setur Antalya** | Antalya | 235 | Mediterranean | 200T travel lift, 30,000m² dry storage |
| **Setur Ayvalık** | Ayvalık, Balıkesir | 200 | North Aegean | Historic area, island access |

**Total Setur:** 3,707 berths (76.2% of network)

**Contact:** seturmarinas.com

---

### 2. **D-Marin** (Global Premium Marina Network)

| Marina | Location | Berths | Region | Special Features |
|--------|----------|--------|--------|-----------------|
| **D-Marin Didim** | Didim, Aydın | 576 | Aegean | 90 superyacht berths, 400T lift, catamaran center |
| **D-Marin Turgutreis** | Turgutreis, Bodrum | 532 | Aegean | 🥇 2024 Gold Award, up to 75m yachts |
| **D-Marin Göcek** | Göcek, Fethiye | 380 | Mediterranean | 🥈 2024 Silver Award, National Park, beach club |

**Total D-Marin (Turkey):** 1,488 berths (30.6% of network)

**Global Portfolio:** 26 marinas across 9 countries | 14,000+ berths worldwide

**Contact:** d-marin.com

---

## 🌍 Geographic Distribution

### **Aegean Coast** (7 marinas, 3,538 berths)
- Setur: Bodrum, Kuşadası, Çeşme, Ayvalık
- D-Marin: Turgutreis, Didim
- **Dominant Region:** 72.7% of total capacity

### **Mediterranean Coast** (4 marinas, 1,088 berths)
- Setur: Kaş, Finike, Antalya
- D-Marin: Göcek
- **Strategic Coverage:** Lycian coast + Antalya

### **Marmara Sea** (1 marina, 240 berths)
- Setur: Yalova
- **Niche Position:** Only non-Istanbul option

---

## 💰 Market Positioning

### **Setur Marinas**
- **Market Position:** National leader, established brand
- **Target Segment:** Mid to high-end leisure + local market
- **Strengths:**
  - Extensive network coverage
  - Strong regional presence
  - Diverse price points
  - Integrated services (fuel, repair, chandlery)

### **D-Marin**
- **Market Position:** Premium global network, luxury focus
- **Target Segment:** International superyachts + HNW individuals
- **Strengths:**
  - Gold Anchor awards
  - Superyacht specialization
  - International brand recognition
  - Reciprocal berth program (14,000+ berths globally)

---

## 🎯 Big-3 Strategy

### Current Status: **2 of 3 Groups Integrated**

1. ✅ **Setur** - National leader (3,707 berths)
2. ✅ **D-Marin** - Global premium (1,488 berths in Turkey)
3. ⏳ **3rd Group TBD** - Candidates:
   - IC Marina (İzmir, Bodrum locations)
   - Ece Marina (Istanbul, Fethiye)
   - Marti Marina (Marmaris, Bodrum)
   - Yalıkavak Marina (Mega yacht focused)

### Integration Benefits

**For Marina Operators:**
- 🤖 AI-powered booking optimization
- 📊 Real-time availability management
- 💰 Dynamic pricing capabilities
- 📈 Revenue optimization (€1.68M/year per large marina - see Kalamış case study)

**For Yacht Owners:**
- 🔍 Multi-network search (4,867+ berths)
- 💳 Unified booking experience
- 🗺️ Complete Turkey coverage
- ⚡ Instant availability confirmation

---

## 🗄️ Database Structure

### Implementation: `backend/database/setur_mock_db.py`

**Architecture:**
- **Class:** `SeturMockDatabase` (implements `DatabaseInterface`)
- **Multi-group support:** Yes (Setur + D-Marin in single database)
- **Auto-generation:** Berths, sections, pricing automatically created per marina
- **ID Convention:**
  - Setur: `setur-{location}-001`
  - D-Marin: `dmarin-{location}-001`

**Key Methods:**
```python
get_all_marinas()                    # Returns all 12 marinas
get_marina_by_id(marina_id)          # Specific marina lookup
search_available_berths(             # Cross-network search
    marina_id=None,                  # Optional: filter by marina
    min_length=None,                 # Boat size filters
    needs_electricity=False,
    needs_water=False
)
```

**Data Models:** (see `backend/database/models.py`)
- `Marina` - Facility info, amenities, coordinates
- `Berth` - Individual berth specs, pricing, status
- `Booking` - Reservation details, customer info

---

## 📡 API Integration Points

### Skill: `BerthManagementSkill`
**Location:** `backend/skills/berth_management_skill.py`

**Supported Operations:**
- `search_berths` - Cross-marina availability search
- `list_marinas` - Get all marinas (Setur + D-Marin)
- `create_booking` - Book any berth in network
- `get_marina_info` - Detailed marina information

**Example Query:**
```
User: "Find me a berth for a 15m yacht in Bodrum area"

Response includes:
- Setur Bodrum Marina (450 berths)
- D-Marin Turgutreis (532 berths)
- Cross-operator comparison
- Price range: €120-€180/day
```

---

## 🔮 Future Expansion

### Phase 3: Complete Big-3
- Research 3rd marina group
- Add to database
- Update documentation

### Phase 4: Advanced Features
- Real-time API integration (replace mock data)
- Dynamic pricing engine
- Weather-based availability
- Seasonal demand forecasting

### Phase 5: International Expansion
- D-Marin global network (Greece, Croatia, UAE, etc.)
- Cross-country booking
- Multi-currency support

---

## 📞 Contact Information

### Setur Marinas
- **Website:** seturmarinas.com
- **Email:** info@seturmarinas.com
- **VHF:** Channel 73 (most locations)

### D-Marin
- **Website:** d-marin.com
- **Email:** info@d-marin.com
- **VHF:** Channel 16/72 (Didim), 73 (others)

---

**Last Updated:** 2025-11-10
**Database Version:** v2.0 (Multi-group)
**Total Marinas:** 12
**Total Berths:** ~4,867
