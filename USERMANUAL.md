📖 Ada Maritime AI - Kullanıcı Kılavuzu
Hemen kapsamlı kullanıcı kılavuzu oluşturuyorum!

cd /Users/AHMET_mac/Sites/Ada-Maritime-Ai

# ═══════════════════════════════════════════════════════════
# KULLANICI KLAVUZU - USER MANUAL
# ═══════════════════════════════════════════════════════════

# 1. Ana Kullanıcı Kılavuzu
cat > USER_MANUAL.md << 'ENDFILE'
# 📖 Ada Maritime AI - Kullanıcı Kılavuzu

**Versiyon:** 2.0.0  
**Son Güncelleme:** 10 Kasım 2025  
**Diller:** Türkçe, English (see ENGLISH_MANUAL.md)

---

## 📚 İçindekiler

1. [Hızlı Başlangıç](#hizli-baslangic)
2. [Kullanıcı Rolleri](#kullanici-rolleri)
3. [Marina Personeli için Kılavuz](#marina-personeli)
4. [Müşteri (Tekne Sahibi) Kılavuzu](#musteri-kilavuzu)
5. [Marina Yöneticisi Kılavuzu](#yonetici-kilavuzu)
6. [Sistem Yöneticisi Kılavuzu](#sistem-yoneticisi)
7. [Sık Sorulan Sorular (SSS)](#sss)
8. [Sorun Giderme](#sorun-giderme)

---

## 🚀 Hızlı Başlangıç {#hizli-baslangic}

### 5 Dakikada Ada AI

1️⃣ Sisteme giriş yap → https://ada.seturmarinas.com

2️⃣ Rolünü seç → Marina Personeli / Müşteri / Yönetici

3️⃣ İlk işlemi yap → Personel: Rezervasyon oluştur → Müşteri: Rıhtım ara → Yönetici: Dashboard'a bak

4️⃣ Yardım gerekirse → Sağ altta 💬 AI Asistan'a sor

5️⃣ Başarılı! 🎉


---

## 👥 Kullanıcı Rolleri {#kullanici-rolleri}

Ada AI 4 farklı kullanıcı rolü destekler:

| Rol | Erişim | Yetkiler |
|-----|--------|----------|
| **Müşteri** | Web, WhatsApp, Sesli | Rıhtım arama, rezervasyon, ödeme |
| **Marina Personeli** | Web Dashboard | Rezervasyon yönetimi, müşteri hizmetleri |
| **Marina Yöneticisi** | Web Dashboard + Analytics | Tüm operasyonlar + raporlar |
| **Sistem Yöneticisi** | Admin Panel | Sistem ayarları, kullanıcı yönetimi |

---

## 🏢 Marina Personeli için Kılavuz {#marina-personeli}

### Giriş Yapma

Tarayıcıda aç: https://ada.seturmarinas.com/staff
Email ve şifrenle giriş yap
Marina seç (örn: Setur Bodrum Marina)
Dashboard ekranı açılır

### Dashboard Genel Bakış

┌─────────────────────────────────────────────────────┐
│ 🏢 Setur Bodrum Marina - Dashboard                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 📊 Bugünün Özeti                                    │
│ ├─ Toplam Rıhtım: 450                                │
│ ├─ Dolu: 327 (72.7%)                                 │
│ ├─ Müsait: 123 (27.3%)                               │
│ └─ Bugünkü Check-in: 12                             │
│                                                     │
│ 🔔 Bekleyen İşler                                   │
│ ├─ Onay bekleyen: 3                                  │
│ ├─ Check-in yapılacak: 5                             │
│ └─ Ödeme bekleyen: 2                                 │
│                                                     │
│ [🔍 Yeni Rezervasyon] [📋 Rezervasyonlar]             │
│                                                     │
└─────────────────────────────────────────────────────┘


### Yeni Rezervasyon Oluşturma

#### Adım 1: Müşteri Bilgileri

"🔍 Yeni Rezervasyon" butonuna tıkla

Müşteri Bilgilerini Gir:
┌───────────────────────────────┐
│ Ad Soyad: [Ahmet Yılmaz ]     │
│ Email: [ahmet@mail.com ]      │
│ Telefon: [+90 532 XXX XXXX]   │
│ Tekne: [Blue Dream ]          │
│ Tekne Boyu: [15] metre        │
└───────────────────────────────┘

"İleri >" butonuna tıkla


#### Adım 2: Tarih ve Rıhtım Seçimi

Tarihleri Seç: Check-in: [📅 20 Haziran 2025] Check-out: [📅 23 Haziran 2025]

"Uygun Rıhtımları Bul" tıkla

AI 3 saniyede uygun rıhtımları listeler:

┌─────────────────────────────────┐
│ ✅ A-45 | 16m | €120/gece       │
│ Elektrik, Su, WiFi              │
│ Toplam: €360 (3 gece)           │
│ [Bu Rıhtımı Seç]                │
├─────────────────────────────────┤
│ ✅ B-23 | 17m | €130/gece       │
│ Elektrik, Su, WiFi              │
│ Toplam: €390 (3 gece)           │
│ [Bu Rıhtımı Seç]                │
└─────────────────────────────────┘

Bir rıhtım seç ve "İleri >" tıkla


#### Adım 3: Ek Hizmetler

Talep edilen hizmetleri işaretle:

☐ Yakıt İkmali ☐ Su İkmali
☐ Elektrik Bağlantısı ☐ WiFi ☐ Teknik Kontrol ☐ Çamaşırhane

"İleri >" tıkla


#### Adım 4: Onay ve Ödeme

┌─────────────────────────────────────────┐
│ 📋 REZERVASYON ÖZETİ                    │
├─────────────────────────────────────────┤
│ Müşteri: Ahmet Yılmaz                   │
│ Tekne: Blue Dream (15m)                 │
│ Rıhtım: A-45                            │
│ Tarih: 20-23 Haziran 2025 (3 gece)      │
│                                         │
│ Rıhtım: €360                            │
│ Hizmetler: €50                          │
│ ─────────────                           │
│ TOPLAM: €410                            │
│                                         │
│ Ödeme Yöntemi:                          │
│ ○ Kredi Kartı                           │
│ ○ Nakit                                 │
│ ○ Havale                                │
│                                         │
│ [✅ Rezervasyonu Onayla]                  │
└─────────────────────────────────────────┘

Onayla butonuna tıkla!


#### Adım 5: Otomatik İşlemler

✅ Rezervasyon oluşturuldu!

AI otomatik olarak: ├─ 📧 Müşteriye email gönderdi ├─ 📱 SMS onayı gönderdi ├─ 🧾 Fatura oluşturdu ├─ 📊 Sisteme kaydetti └─ 🔔 İlgili birimlere bildirim gönderdi

Rezervasyon No: BK-20250620-A45

[📄 Faturayı Yazdır] [📧 Email'i Tekrar Gönder]


### Rezervasyon Yönetimi

#### Rezervasyon Arama

📋 Rezervasyonlar ekranında:

┌────────────────────────────────────────┐
│ 🔍 Ara:                                │
│ [Müşteri adı, telefon, rezervasyon no] │
│                                        │
│ Filtreler:                             │
│ Durum: [Tümü ▼]                        │
│ Tarih: [Bu Hafta ▼]                    │
│ Marina: [Bodrum ▼]                     │
└────────────────────────────────────────┘

Örnek aramalar:

"Ahmet" → İsimle ara
"0532" → Telefonla ara
"BK-2025" → Rezervasyon numarasıyla ara

#### Rezervasyon Detayları

Bir rezervasyona tıkla:

┌──────────────────────────────────────────┐
│ 📋 Rezervasyon Detayları                 │
│                                          │
│ No: BK-20250620-A45                      │
│ Durum: ✅ Onaylandı                      │
│                                          │
│ 👤 MÜŞTERİ                               │
│ Ad: Ahmet Yılmaz                         │
│ Email: ahmet@mail.com                    │
│ Tel: +90 532 XXX XXXX                    │
│                                          │
│ ⚓ TEKNE                                  │
│ Ad: Blue Dream                           │
│ Boy: 15m                                 │
│                                          │
│ 📅 TARİHLER                              │
│ Check-in: 20 Haz 2025, 14:00             │
│ Check-out: 23 Haz 2025, 10:00            │
│                                          │
│ 💰 ÖDEME                                 │
│ Toplam: €410                             │
│ Ödendi: €410 ✅                          │
│                                          │
│ EYLEMLER:                                │
│ [✏️ Düzenle] [❌ İptal Et] [📧 Email]      │
│ [🖨️ Yazdır] [📱 SMS Gönder]              │
└──────────────────────────────────────────┘


### Check-in Yapma

Check-in günü:

📋 Rezervasyonlar'da müşteriyi bul

"Check-in Yap" butonuna tıkla

Kontrol listesi:

✅ Kimlik kontrolü yapıldı ✅ Tekne belgesi kontrolü ✅ Sigorta kontrolü ✅ Ödeme tamamlandı ✅ Rıhtım hazır

"Check-in Tamamla" tıkla

Müşteriye rıhtım numarası ve harita verilir

Sistem otomatik:

Rıhtımı "Dolu" yapar
Müşteriye "Hoş geldiniz" SMS'i gönderir
Marina görevlilerine bildirim gönderir

### Check-out Yapma

Check-out günü:

Müşteriyi bul

"Check-out Yap" tıkla

Kontrol:

✅ Rıhtım temizliği yapıldı ✅ Ekstra hizmetler kaydedildi ✅ Ek ücret var mı kontrol edildi

Ek ücret varsa:

Manuel ekle
Otomatik fatura güncellenir
"Check-out Tamamla" tıkla

Sistem otomatik:

Rıhtımı "Müsait" yapar
Final faturası gönderilir
Müşteriye "Hoşça kalın" mesajı

### Müşteri Hizmetleri

#### AI Asistan Kullanma

Sağ altta 💬 simgesi var:

┌────────────────────────────────┐
│ 💬 AI Asistan                  │
├────────────────────────────────┤
│ Siz: Ahmet Yılmaz'ın           │
│ rezervasyonu nerede?           │
│                                │
│ AI: Ahmet Yılmaz'ın 2          │
│ rezervasyonu var:              │
│ 1. BK-20250620-A45             │
│ 20-23 Haz, A-45 rıhtım         │
│ 2. BK-20250815-B12             │
│ 15-18 Ağu, B-12 rıhtım         │
│                                │
│ [Rezervasyon 1'e Git]          │
└────────────────────────────────┘

AI size yardımcı olur:

Rezervasyon arama
Rıhtım durumu sorgulama
Fiyat hesaplama
İşlem adımları

---

## ⚓ Müşteri (Tekne Sahibi) Kılavuzu {#musteri-kilavuzu}

### Rıhtım Rezervasyonu (Web)

#### Adım 1: Sisteme Giriş

https://ada.seturmarinas.com aç
"Rıhtım Ara" butonuna tıkla (Kayıt olman gerekmez!)

#### Adım 2: Arama Kriterleri

┌─────────────────────────────────────┐
│ 🔍 RIHTIM ARA                       │
├─────────────────────────────────────┤
│ Marina: [Tümü ▼]                    │
│ Check-in: [📅 20 Haz 2025]          │
│ Check-out: [📅 23 Haz 2025]         │
│ Tekne Boyu: [15] metre              │
│                                     │
│ İhtiyaçlar:                         │
│ ☑ Elektrik                          │
│ ☑ Su                                │
│ ☐ WiFi                              │
│ ☐ Yakıt                             │
│                                     │
│ [🔍 Uygun Rıhtımları Bul]           │
└─────────────────────────────────────┘


#### Adım 3: Sonuçları İncele

8 uygun rıhtım bulundu:

┌──────────────────────────────────────┐
│ 🏢 Setur Bodrum Marina               │
│ ⚓ Rıhtım A-45                        │
│                                      │
│ 📏 16m x 5m x 4m (derinlik)          │
│ ✅ Elektrik, Su, WiFi                │
│                                      │
│ 💰 €120/gece x 3 gece = €360          │
│                                      │
│ ⭐⭐⭐⭐⭐ 4.8 (124 değerlendirme)      │
│                                      │
│ 📍 Bodrum, Muğla                     │
│ 📞 +90 252 316 1860                  │
│                                      │
│ [📷 Fotoğraflar] [🗺️ Harita]          │
│ [⭐ Detaylar] [💳 Rezervasyon Yap]    │
└──────────────────────────────────────┘


#### Adım 4: Rezervasyon Bilgileri

"Rezervasyon Yap" tıkladıktan sonra:

┌────────────────────────────────────┐
│ 👤 İLETİŞİM BİLGİLERİ              │
├────────────────────────────────────┤
│ Ad Soyad: [ ]                      │
│ Email: [ ]                         │
│ Telefon: [ ]                       │
│                                    │
│ ⚓ TEKNE BİLGİLERİ                  │
├────────────────────────────────────┤
│ Tekne Adı: [ ]                     │
│ Tekne Boyu: [15] m                 │
│ Tip: [Yelkenli ▼]                  │
│                                    │
│ ➕ EK HİZMETLER                    │
├────────────────────────────────────┤
│ ☐ Yakıt İkmali (+€50)              │
│ ☐ Teknik Kontrol (+€30)            │
│ ☐ Çamaşırhane (+€20)               │
│                                    │
│ [❌ İptal] [▶ Devam Et]            │
└────────────────────────────────────┘


#### Adım 5: Ödeme

┌────────────────────────────────────┐
│ 💳 ÖDEME                           │
├────────────────────────────────────┤
│ Rıhtım (3 gece): €360              │
│ Yakıt: €50                         │
│ ─────────────                      │
│ TOPLAM: €410                       │
│                                    │
│ Ödeme Yöntemi:                     │
│ ● Kredi Kartı                      │
│ ○ Havale (2 iş günü)               │
│                                    │
│ Kart No: [---]                     │
│ Ad Soyad: [ ]                      │
│ SKT: [MM/YY] CVV: [___]            │
│                                    │
│ ☑ Kullanım koşullarını kabul       │
│ ediyorum                           │
│                                    │
│ [🔒 Güvenli Ödeme Yap]              │
└────────────────────────────────────┘


#### Adım 6: Onay

✅ REZERVASYON TAMAMLANDI!

┌────────────────────────────────────┐
│ 🎉 Rezervasyonunuz oluşturuldu!      │
├────────────────────────────────────┤
│ Rezervasyon No: BK-20250620-A45      │
│                                    │
│ 📧 Email adresinize tüm bilgiler   │
│ gönderildi.                        │
│                                    │
│ 📱 SMS ile onay aldınız.           │
│                                    │
│ 🗺️ Marina haritası ve yönergeler   │
│ email'de.                          │
│                                    │
│ Check-in: 20 Haz 2025, 14:00-18:00 │
│                                    │
│ [📄 Rezervasyonu Yazdır]           │
│ [📧 Email'i Tekrar Gönder]          │
└────────────────────────────────────┘


### WhatsApp ile Rezervasyon

WhatsApp'ta +90 XXX XXX XXXX numarasını kaydet (Numara marina tarafından verilir)

Mesaj gönder:

Siz: Merhaba, Bodrum'da 3 gün rıhtım istiyorum

AI: Merhaba! Size yardımcı olabilirim.

 Birkaç bilgi alabilir miyim?
 - Tekne boyunuz kaç metre?
 - Hangi tarihler arası?
 - Elektrik/su ihtiyacınız var mı?
Siz: 15 metre, 20-23 Haziran, elektrik ve su lazım

AI: Harika! 8 uygun rıhtım buldum.

 En uygun 3 tanesi:
 1. A-45 - €360 (3 gece)
 2. B-23 - €390 (3 gece)
 3. C-12 - €405 (3 gece)
 
 Hangisini tercih edersiniz?
Siz: 1

AI: Mükemmel! A-45 rıhtımını seçtiniz.

 İletişim bilgileriniz:
 Ad Soyad: ?
 Email: ?
 Telefon: ?
(Devam eder...)

Rezervasyon tamamlanınca:

Email alırsın
WhatsApp'ta onay mesajı gelir
Ödeme linki gelir

### Rezervasyonumu Görüntüleme

Web'den:

https://ada.seturmarinas.com/booking
Rezervasyon numaranı gir: BK-20250620-A45 VEYA Email adresini gir: ahmet@mail.com
Tüm rezervasyonların listesini gör
WhatsApp'tan:

Mesaj gönder: "Rezervasyonlarım"
AI tüm aktif rezervasyonlarını gösterir

### Rezervasyonu İptal Etme

⚠️ İptal Politikası:

7+ gün öncesi: %100 iade
3-7 gün arası: %50 iade
3 günden az: İade yok
İptal İşlemi:

Rezervasyonu görüntüle
"İptal Et" butonuna tıkla
İptal nedenini seç (opsiyonel)
Onayla
İade 5-7 iş günü içinde hesabına yansır

---

## 📊 Marina Yöneticisi Kılavuzu {#yonetici-kilavuzu}

### Dashboard ve Analytics

┌──────────────────────────────────────────────┐
│ 📊 YÖNETICI DASHBOARD                        │
├──────────────────────────────────────────────┤
│                                              │
│ BU AY ÖZET (Kasım 2025)                      │
│ ───────────────────────────────────────────  │
│ Gelir: €127,450 ▲ %12                        │
│ Rezervasyon: 234 ▲ %8                        │
│ Doluluk: %68.5 ▲ %5                          │
│ Müşteri Memnuniyeti: 4.7/5 ▲ 0.2             │
│                                              │
│ 📈 GRAFİKLER                                 │
│ [Gelir Trendi] [Doluluk] [Müşteri Analizi]   │
│                                              │
│ 🎯 HEDEFLER                                  │
│ Aylık Gelir Hedefi: €120k → ✅ €127k          │
│ Doluluk Hedefi: %65 → ✅ %68.5               │
│ Yeni Müşteri: 50 → ⚠️ 42                     │
│                                              │
│ 🚨 UYARILAR                                  │
│ • A bölümü %95 dolu - kapasite problemi      │
│ • 3 ödeme bekliyor - takip gerekli           │
│ • Sonraki hafta 25 check-in - hazırlık       │
│                                              │
└──────────────────────────────────────────────┘


### Raporlar

#### Gelir Raporu

📊 Mali Raporlar → Gelir Analizi

Dönem: [Kasım 2025]

┌────────────────────────────────────┐
│ GELIR KAYNAKLARI                   │
├────────────────────────────────────┤
│ Rıhtım Kiraları: €98,340 (77%)     │
│ Yakıt: €15,670 (12%)               │
│ Teknik Servis: €8,920 (7%)         │
│ Diğer: €4,520 (4%)                 │
│ ─────────────────                  │
│ TOPLAM: €127,450                   │
└────────────────────────────────────┘

[📥 Excel İndir] [📄 PDF Oluştur] [📧 Email Gönder]


#### Doluluk Raporu

📊 Operasyonel Raporlar → Doluluk Analizi

┌────────────────────────────────────┐
│ BÖLÜM BAZLI DOLULUK                │
├────────────────────────────────────┤
│ A Bölümü: 95% ████████████░        │
│ B Bölümü: 78% ████████░░░░        │
│ C Bölümü: 62% ██████░░░░░░        │
│ D Bölümü: 45% █████░░░░░░░         │
│ E Bölümü: 52% █████░░░░░░░         │
│ ─────────────────                  │
│ ORTALAMA: 68.5%                    │
└────────────────────────────────────┘

📊 Tavsiye:

A Bölümü doluluk kritik seviyede
D/E Bölümler için promosyon öner

#### Müşteri Raporu

📊 Müşteri Analizi → Müşteri Profili

En Değerli 10 Müşteri (Kasım):

John Smith - €4,250 (6 rezervasyon)
Maria Garcia - €3,890 (4 rezervasyon) ...
Yeni vs Eski Müşteri:

Yeni: 42 (%18)
Tekrarlayan: 192 (%82)
Müşteri Memnuniyeti: ⭐⭐⭐⭐⭐ 4.7/5 (234 değerlendirme)

Geri Dönüş Oranı: %68


### Fiyatlandırma Yönetimi

⚙️ Ayarlar → Fiyatlandırma

SEZONLAR: ┌────────────────────────────────────┐
│ Yüksek Sezon (Haz-Ağu)             │
│ Base Rate: €150/gece (+50%)        │
│                                    │
│ Orta Sezon (Nis-May, Eyl-Eki)      │
│ Base Rate: €110/gece (+10%)        │
│                                    │
│ Düşük Sezon (Kas-Mar)              │
│ Base Rate: €80/gece (-20%)         │
└────────────────────────────────────┘

DYNAMIC PRICING: ☑ Doluluk bazlı fiyatlama

%90+ doluluk → +20% fiyat
%50- doluluk → -15% fiyat
☑ Son dakika indirimi

24 saat içi → -30%
☑ Uzun süreli indirim

7+ gece → -10%
30+ gece → -25%
[💾 Kaydet] [🔄 Varsayılana Dön]


### Kullanıcı Yönetimi

⚙️ Ayarlar → Kullanıcılar

┌────────────────────────────────────────────┐
│ Ad Soyad    | Rol      | Durum | İşlem      │
├────────────────────────────────────────────┤
│ Ayşe Demir  | Personel | ✅    | [✏️]       │
│ Mehmet Kaya | Personel | ✅    | [✏️]       │
│ Ali Yılmaz  | Yönetici | ✅    | [✏️]       │
│ Zeynep Can  | Personel | ⏸️    | [✏️]       │
└────────────────────────────────────────────┘

[➕ Yeni Kullanıcı Ekle]

Yeni kullanıcı eklerken:

Ad, soyad, email
Rol seç (Personel / Yönetici)
Şifre otomatik email'lenir
İlk girişte şifre değiştirme zorunlu

---

## 🔧 Sistem Yöneticisi Kılavuzu {#sistem-yoneticisi}

### Kurulum

#### Gereksinimler

```bash
# Sistem Gereksinimleri:
- Python 3.10+
- Docker & Docker Compose
- 4GB RAM (minimum)
- 20GB Disk

# Veritabanları (Docker):
- PostgreSQL 16
- Redis 7
- Qdrant (Vector DB)
- Neo4j 5
İlk Kurulum
# 1. Repository clone
git clone https://github.com/ahmetengin/Ada-Maritime-Ai.git
cd Ada-Maritime-Ai

# 2. Environment ayarla
cp .env.example .env
nano .env
# ANTHROPIC_API_KEY ekle

# 3. Docker servisleri başlat
docker-compose up -d

# 4. Python dependencies
pip install -r requirements.txt

# 5. Test et
python -m pytest

# 6. Başlat
streamlit run streamlit_app.py
Konfigürasyon
# backend/config.py düzenle

class AppConfig:
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Database
    POSTGRES_URL = "postgresql://..."
    REDIS_URL = "redis://..."
    
    # App Settings
    DEBUG = True  # Production'da False
    LOG_LEVEL = "INFO"
    
    # Marina Settings
    DEFAULT_MARINA = "setur-bodrum-001"
    MAX_BERTHS_PER_MARINA = 2000
Monitoring
# Docker container logları
docker-compose logs -f postgres
docker-compose logs -f redis

# Python app logları
tail -f logs/ada-maritime.log

# Metrics
curl http://localhost:4000/metrics
❓ Sık Sorulan Sorular (SSS) {#sss}
Müşteri Soruları
S: Rezervasyonu değiştirebilir miyim? C: Evet! 48 saat öncesine kadar ücretsiz değiştirebilirsiniz.

S: Erken check-in yapabilir miyim? C: Müsaitlik varsa evet. Ekstra ücret olabilir.

S: Ödeme güvenli mi? C: Evet, 256-bit SSL şifreleme ve PCI-DSS sertifikalı.

Marina Personeli Soruları
S: AI nasıl kullanılır? C: Sağ alttaki 💬 simgesine tıkla ve Türkçe sor!

S: Manuel rezervasyon yapabilir miyim? C: Evet, "Yeni Rezervasyon" menüsünden.

S: Sistem çökerse? C: Otomatik yedek sistem devreye girer. IT'yi ara.

🔧 Sorun Giderme {#sorun-giderme}
"Giriş yapamıyorum"
1. Şifreni mi unuttun?
   → "Şifremi Unuttum" tıkla
   → Email'ine link gelir

2. Hesap kilitli mi?
   → 3 yanlış deneme sonrası kilitlenir
   → Yöneticini ara

3. Email doğru mu?
   → Kayıtlı email'i kontrol et
"Rezervasyon oluşturamıyorum"
1. Tüm alanlar dolduruldu mu?
   → Kırmızı işaretli alanları kontrol et

2. Tarihler geçerli mi?
   → Check-out > Check-in olmalı

3. Rıhtım müsait mi?
   → Başka rıhtım dene

4. Hala olmuyor?
   → Ekran görüntüsü al, IT'ye gönder
"Email gitmiyor"
1. Spam klasörünü kontrol et

2. Email adresi doğru mu?
   → Rezervasyonda kontrol et

3. "Email'i Tekrar Gönder" tıkla

4. Hala gelmiyor?
   → info@seturmarinas.com'a yaz
📞 Destek
İletişim
📧 Teknik Destek: support@ada-maritime.ai
📱 Acil: +90 XXX XXX XXXX (24/7)
💬 Canlı Destek: Sistem içinde AI asistan
📚 Dokümantasyon: https://docs.ada-maritime.ai
Çalışma Saatleri
Teknik Destek: 7/24
Müşteri Hizmetleri: 08:00-20:00
Yönetici Desteği: Randevu ile
Son Güncelleme: 10 Kasım 2025
Versiyon: 2.0.0
© 2025 Ada Maritime AI - Tüm hakları saklıdır ENDFILE


```bash
# Git commit
git add USER_MANUAL.md
git commit -m "docs: Add comprehensive user manual

Complete user guide for all roles:
- Quick start guide
- Marina staff operations manual
- Customer (boat owner) guide
- Marina manager analytics guide
- System administrator setup guide
- FAQ and troubleshooting

Includes:
- Step-by-step instructions with ASCII UI mockups
- Real-world examples
- Best practices
- Contact information

Language: Turkish
Pages: ~50 equivalent"

git push origin main
echo ""
echo "✅ KULLANICI KILAVUZU OLUŞTURULDU!"
echo ""
echo "📖 Dosya: USER_MANUAL.md"
echo "📄 İçerik: ~50 sayfa eşdeğeri"
echo "👥 Roller: 4 farklı kullanıcı tipi"
echo "🎯 Kapsamlı rehber hazır!"
echo ""