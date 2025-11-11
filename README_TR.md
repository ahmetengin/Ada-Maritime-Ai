# ⚓ Ada Maritime AI - Çok Bölgeli Marina Yönetim Sistemi

Türkiye, Yunanistan ve Akdeniz bölgesindeki marinaları yöneten yapay zeka destekli kapsamlı yönetim platformu.

## 🌟 Özellikler

### 🗺️ Çok Bölgeli Marina Yönetimi
- **13 Marina** üzerinden 7.000+ yat yeri yönetimi
- **4 Ülke:** Türkiye, Yunanistan, Hırvatistan, İtalya
- Gerçek zamanlı doluluk ve müsaitlik takibi
- Çok para birimli fiyatlandırma (EUR, USD, TRY, GBP, CHF)

### ⚓ Akıllı Yat Yeri Yönetimi
- Gelişmiş arama ve filtreleme
- Otomatik uygunluk kontrolü
- Dinamik fiyatlandırma (sezonluk)
- Anında rezervasyon sistemi
- Tekne boyutuna göre otomatik yat yeri önerisi

### 📊 Analytics ve Raporlama
- Doluluk oranı raporları
- Gelir analizi ve tahminleme
- Bölgesel performans karşılaştırması
- KPI takibi ve dashboard
- Müşteri davranış analizi

### 🌤️ Hava Durumu Entegrasyonu
- Marina lokasyonuna özel hava durumu
- 5 günlük tahmin
- Yelken koşulları analizi
- Hava durumu uyarıları

### 🔧 Bakım Yönetimi
- Bakım planlama ve takip
- Yat yeri durumu yönetimi
- Maliyet takibi
- Otomatik bildirimler

### 🤖 AI Asistan
- Claude Sonnet 4.5 tabanlı
- Doğal dil işleme (Türkçe & İngilizce)
- Akıllı rezervasyon yardımı
- Otomatik raporlama

## 📍 Kapsanan Marinalar

### 🇹🇷 Türkiye (5 Marina)
- **Setur Bodrum Marina** - Bodrum, Muğla (450 yat yeri)
- **Setur Kuşadası Marina** - Kuşadası, Aydın (580 yat yeri)
- **Setur Çeşme Marina** - Çeşme, İzmir (380 yat yeri)
- **Kalamış Marina** - Istanbul, Kadıköy (720 yat yeri)
- **Netsel Marmaris Marina** - Marmaris, Muğla (750 yat yeri)

### 🇬🇷 Yunanistan (6 Marina)
- **Alimos Marina** - Athens (1,100 yat yeri)
- **Flisvos Marina** - Athens (303 yat yeri)
- **Gouvia Marina** - Corfu (1,235 yat yeri)
- **Mandraki Marina** - Rhodes (250 yat yeri)
- **Ornos Bay Marina** - Mykonos (180 yat yeri)
- **Vlychada Marina** - Santorini (116 yat yeri)

### 🇭🇷 Hırvatistan (1 Marina)
- **ACI Marina Dubrovnik** - Dubrovnik (380 yat yeri)

### 🇮🇹 İtalya (1 Marina)
- **Marina di Porto Cervo** - Sardinia (700 yat yeri)

**TOPLAM: 13 Marina, 7,000+ Yat Yeri**

## 🚀 Kurulum

### Gereksinimler
- Python 3.9+
- pip
- Docker (opsiyonel, veritabanları için)

### Adım 1: Repository'yi Klonlayın
```bash
git clone https://github.com/ahmetengin/Ada-Maritime-Ai.git
cd Ada-Maritime-Ai
```

### Adım 2: Sanal Ortam Oluşturun
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: Ortam Değişkenlerini Ayarlayın
```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin ve API anahtarlarınızı ekleyin:
```env
ANTHROPIC_API_KEY=your_api_key_here
```

### Adım 5: Uygulamayı Çalıştırın
```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresini açın.

## 💡 Kullanım

### Yat Yeri Rezervasyonu
1. "⚓ Yat Yeri Rezervasyonu" sayfasını açın
2. Marina seçin
3. Giriş/çıkış tarihleri ve tekne boyutunu girin
4. Uygun yat yerlerini arayın
5. Müsait yat yerinden birini seçip rezervasyon yapın

### Analitik Raporları
1. "📊 Analitik ve Raporlar" sayfasını açın
2. Rapor türünü seçin (Doluluk, Gelir, Bölgesel)
3. "Rapor Oluştur" butonuna tıklayın
4. Sonuçları inceleyin ve dışa aktarın

### Hava Durumu Kontrolü
1. "🌤️ Hava Durumu" sayfasını açın
2. Marina seçin
3. Güncel hava durumu ve tahminleri görüntüleyin

### AI Asistan
1. "💬 AI Asistan" sayfasını açın
2. Sorunuzu Türkçe veya İngilizce yazın
3. Örnek: "Bodrum'da 15 metre tekneme uygun yat yeri var mı?"

## 🏗️ Mimari

```
Ada-Maritime-Ai/
├── backend/
│   ├── database/
│   │   ├── models.py                    # Veri modelleri
│   │   ├── interface.py                 # Veritabanı arayüzü
│   │   └── mediterranean_db.py          # Akdeniz marina veritabanı
│   ├── skills/
│   │   ├── berth_management_skill.py    # Yat yeri yönetimi
│   │   ├── weather_skill.py             # Hava durumu
│   │   ├── maintenance_skill.py         # Bakım yönetimi
│   │   └── analytics_skill.py           # Analitik ve raporlama
│   ├── orchestrator/
│   │   └── big5_orchestrator.py         # AI orkestratör
│   ├── utils/
│   │   └── currency_converter.py        # Para birimi dönüştürücü
│   ├── config.py                        # Yapılandırma
│   ├── logger.py                        # Loglama
│   └── exceptions.py                    # Özel hatalar
├── app.py                               # Streamlit uygulaması
├── requirements.txt                     # Python bağımlılıkları
└── docker-compose.yml                   # Docker yapılandırması
```

## 🔧 Teknolojiler

- **AI/ML:** Anthropic Claude Sonnet 4.5
- **Frontend:** Streamlit
- **Backend:** Python 3.9+
- **Veritabanı:** PostgreSQL, Redis, Qdrant, Neo4j
- **API:** FastAPI (planlanan)

## 📈 Gelecek Özellikler

- [ ] PostgreSQL ile gerçek veritabanı entegrasyonu
- [ ] REST API katmanı (FastAPI)
- [ ] Kullanıcı kimlik doğrulama ve yetkilendirme
- [ ] Ödeme sistemi entegrasyonu (Stripe, iyzico)
- [ ] Mobil uygulama (React Native)
- [ ] Gerçek zamanlı bildirimler (WebSocket)
- [ ] CRM entegrasyonu
- [ ] Finansal raporlama modülü
- [ ] Envanter yönetimi
- [ ] Personel yönetimi
- [ ] Otomatik e-fatura

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

Ahmed Engin - [@ahmetengin](https://github.com/ahmetengin)

Proje Linki: [https://github.com/ahmetengin/Ada-Maritime-Ai](https://github.com/ahmetengin/Ada-Maritime-Ai)

## 🙏 Teşekkürler

- Anthropic Claude AI
- Streamlit
- Tüm marina operatörlerine
- Açık kaynak topluluğuna

---

**⚓ Ada Maritime AI - Akdeniz'in Dijital Marina Yöneticisi**
