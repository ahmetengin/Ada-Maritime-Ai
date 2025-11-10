# ⚓ Ada Maritime AI - Multi-Region Marina Management System

AI-powered comprehensive marina management platform for Turkey, Greece, and Mediterranean region.

[🇹🇷 Türkçe Dokümantasyon](./README_TR.md)

## 🌟 Key Features

### 🗺️ Multi-Region Marina Management
- **13 Marinas** managing 7,000+ berths
- **4 Countries:** Turkey, Greece, Croatia, Italy
- Real-time occupancy and availability tracking
- Multi-currency pricing (EUR, USD, TRY, GBP, CHF)

### ⚓ Smart Berth Management
- Advanced search and filtering
- Automatic suitability checking
- Dynamic pricing (seasonal)
- Instant reservation system
- AI-powered berth recommendations

### 📊 Analytics & Reporting
- Occupancy rate reports
- Revenue analysis and forecasting
- Regional performance comparison
- KPI tracking dashboard
- Customer behavior insights

### 🌤️ Weather Integration
- Location-specific weather data
- 5-day forecasts
- Sailing conditions analysis
- Weather alerts and warnings

### 🔧 Maintenance Management
- Maintenance scheduling and tracking
- Berth status management
- Cost tracking
- Automated notifications

### 🤖 AI Assistant
- Claude Sonnet 4.5 powered
- Natural language processing (Turkish & English)
- Smart booking assistance
- Automated reporting

## 📍 Covered Marinas

### 🇹🇷 Turkey (5 Marinas)
- **Setur Bodrum Marina** - Bodrum, Muğla (450 berths)
- **Setur Kuşadası Marina** - Kuşadası, Aydın (580 berths)
- **Setur Çeşme Marina** - Çeşme, İzmir (380 berths)
- **Kalamış Marina** - Istanbul, Kadıköy (720 berths)
- **Netsel Marmaris Marina** - Marmaris, Muğla (750 berths)

### 🇬🇷 Greece (6 Marinas)
- **Alimos Marina** - Athens (1,100 berths)
- **Flisvos Marina** - Athens (303 berths)
- **Gouvia Marina** - Corfu (1,235 berths)
- **Mandraki Marina** - Rhodes (250 berths)
- **Ornos Bay Marina** - Mykonos (180 berths)
- **Vlychada Marina** - Santorini (116 berths)

### 🇭🇷 Croatia (1 Marina)
- **ACI Marina Dubrovnik** - Dubrovnik (380 berths)

### 🇮🇹 Italy (1 Marina)
- **Marina di Porto Cervo** - Sardinia (700 berths)

**TOTAL: 13 Marinas, 7,000+ Berths**

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip
- Docker (optional, for databases)

### Installation

```bash
# Clone the repository
git clone https://github.com/ahmetengin/Ada-Maritime-Ai.git
cd Ada-Maritime-Ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# Run the application
streamlit run app.py
```

Open your browser at `http://localhost:8501`

## 📚 Documentation

- [Turkish Documentation (Türkçe)](./README_TR.md)
- [API Documentation](./docs/API.md) (coming soon)
- [Architecture Guide](./docs/ARCHITECTURE.md) (coming soon)

## 🏗️ Architecture

```
Ada-Maritime-Ai/
├── backend/
│   ├── database/          # Data models and database layer
│   ├── skills/            # Modular skill system
│   ├── orchestrator/      # AI orchestration
│   ├── utils/             # Utilities (currency converter, etc.)
│   └── services/          # Supporting services
├── app.py                 # Streamlit web application
├── requirements.txt       # Python dependencies
└── docker-compose.yml     # Infrastructure setup
```

## 🔧 Technology Stack

- **AI/ML:** Anthropic Claude Sonnet 4.5
- **Frontend:** Streamlit
- **Backend:** Python 3.9+
- **Databases:** PostgreSQL, Redis, Qdrant, Neo4j
- **API:** FastAPI (planned)

## 🎯 Use Cases

1. **Marina Operators:** Manage multiple marinas across regions
2. **Boat Owners:** Find and book berths easily
3. **Marina Networks:** Centralized management platform
4. **Regional Authorities:** Monitor and analyze marina operations
5. **Investors:** Performance tracking and analytics

## 📊 Supported Operations

### Berth Management
- Search available berths
- Create bookings
- Manage berth status
- Track occupancy

### Weather & Conditions
- Current weather at marina locations
- 5-day forecasts
- Sailing conditions analysis
- Weather alerts

### Maintenance
- Schedule maintenance tasks
- Track maintenance records
- Cost management
- Status updates

### Analytics
- Occupancy reports
- Revenue analysis
- Regional overview
- Performance metrics
- Customer insights

## 🌐 Multi-Currency Support

Supported currencies:
- EUR (Euro) - Base currency
- USD (US Dollar)
- GBP (British Pound)
- TRY (Turkish Lira)
- CHF (Swiss Franc)

## 📈 Roadmap

- [ ] Real database integration (PostgreSQL)
- [ ] REST API layer (FastAPI)
- [ ] User authentication & authorization
- [ ] Payment gateway integration (Stripe, iyzico)
- [ ] Mobile app (React Native)
- [ ] Real-time notifications (WebSocket)
- [ ] CRM integration
- [ ] Financial reporting module
- [ ] Inventory management
- [ ] Staff management
- [ ] Automated invoicing

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Contact

Ahmed Engin - [@ahmetengin](https://github.com/ahmetengin)

Project Link: [https://github.com/ahmetengin/Ada-Maritime-Ai](https://github.com/ahmetengin/Ada-Maritime-Ai)

## 🙏 Acknowledgments

- Anthropic Claude AI
- Streamlit
- All marina operators
- Open source community

---

**⚓ Ada Maritime AI - The Digital Marina Manager for the Mediterranean**

Made with ❤️ for the maritime industry
