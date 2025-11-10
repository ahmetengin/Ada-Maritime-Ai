"""
Ada Maritime AI - Comprehensive Multi-Region Marina Management System
Streamlit Web Application for managing marinas across Turkey, Greece, and Mediterranean
"""

import streamlit as st
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Backend imports
from backend.database.mediterranean_db import get_mediterranean_database
from backend.orchestrator.big5_orchestrator import Big5Orchestrator, AgentContext
from backend.skills.berth_management_skill import BerthManagementSkill
from backend.skills.weather_skill import WeatherSkill
from backend.skills.maintenance_skill import MaintenanceSkill
from backend.skills.analytics_skill import AnalyticsSkill
from backend.utils.currency_converter import get_currency_converter, format_currency
from backend.logger import setup_logger

logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Ada Maritime AI - Multi-Region Marina Management",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0D47A1;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


# Initialize database and skills
@st.cache_resource
def initialize_system():
    """Initialize the marina management system"""
    logger.info("Initializing Ada Maritime AI system...")

    # Initialize database
    db = get_mediterranean_database()

    # Initialize skills
    berth_skill = BerthManagementSkill(db)
    weather_skill = WeatherSkill(db)
    maintenance_skill = MaintenanceSkill(db)
    analytics_skill = AnalyticsSkill(db)

    # Initialize orchestrator
    orchestrator = Big5Orchestrator()
    orchestrator.register_skill(berth_skill)
    orchestrator.register_skill(weather_skill)
    orchestrator.register_skill(maintenance_skill)
    orchestrator.register_skill(analytics_skill)

    logger.info("System initialized successfully")

    return db, orchestrator


# Initialize system
database, orchestrator = initialize_system()
currency_converter = get_currency_converter()


def main():
    """Main application"""

    # Header
    st.markdown('<div class="main-header">⚓ Ada Maritime AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 1.1rem;">'
        'Türkiye, Yunanistan ve Akdeniz Bölgesi Marina Yönetim Sistemi'
        '</p>',
        unsafe_allow_html=True
    )

    # Sidebar navigation
    st.sidebar.title("🧭 Navigasyon")

    page = st.sidebar.radio(
        "Sayfa Seçin",
        [
            "🏠 Ana Sayfa",
            "🗺️ Marinalar",
            "⚓ Yat Yeri Rezervasyonu",
            "📊 Analitik ve Raporlar",
            "🌤️ Hava Durumu",
            "🔧 Bakım Yönetimi",
            "💬 AI Asistan",
        ]
    )

    # Page routing
    if page == "🏠 Ana Sayfa":
        show_home_page()
    elif page == "🗺️ Marinalar":
        show_marinas_page()
    elif page == "⚓ Yat Yeri Rezervasyonu":
        show_booking_page()
    elif page == "📊 Analitik ve Raporlar":
        show_analytics_page()
    elif page == "🌤️ Hava Durumu":
        show_weather_page()
    elif page == "🔧 Bakım Yönetimi":
        show_maintenance_page()
    elif page == "💬 AI Asistan":
        show_ai_assistant_page()


def show_home_page():
    """Display home page with overview"""
    st.markdown('<div class="sub-header">📊 Genel Bakış</div>', unsafe_allow_html=True)

    # Get all marinas
    marinas = database.get_all_marinas()

    # Group by country
    countries = {}
    for marina in marinas:
        if marina.country not in countries:
            countries[marina.country] = []
        countries[marina.country].append(marina)

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Toplam Marina", len(marinas))

    with col2:
        st.metric("Ülkeler", len(countries))

    with col3:
        total_berths = sum(m.total_berths for m in marinas)
        st.metric("Toplam Yat Yeri", total_berths)

    with col4:
        available_berths = sum(m.available_berths for m in marinas)
        st.metric("Müsait Yat Yeri", available_berths)

    st.markdown("---")

    # Regional overview
    st.markdown('<div class="sub-header">🌍 Bölgesel Dağılım</div>', unsafe_allow_html=True)

    for country, country_marinas in countries.items():
        with st.expander(f"🇹🇷 {country} - {len(country_marinas)} Marina", expanded=True):
            for marina in country_marinas:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**{marina.name}**")
                    st.write(f"📍 {marina.city}, {marina.country}")

                with col2:
                    st.write(f"Toplam: {marina.total_berths}")
                    st.write(f"Müsait: {marina.available_berths}")

                with col3:
                    occupancy = marina.occupancy_rate
                    st.write(f"Doluluk: **{occupancy:.1f}%**")
                    if occupancy >= 75:
                        st.write("🟢 Yüksek")
                    elif occupancy >= 50:
                        st.write("🟡 Orta")
                    else:
                        st.write("🔵 Düşük")

                st.markdown("---")


def show_marinas_page():
    """Display marinas page"""
    st.markdown('<div class="sub-header">🗺️ Marina Rehberi</div>', unsafe_allow_html=True)

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        countries = list(set(m.country for m in database.get_all_marinas()))
        selected_country = st.selectbox("Ülke", ["Tümü"] + countries)

    with col2:
        amenities = ["Restoran", "Yakıt", "Wifi", "Teknik Servis", "Spa"]
        selected_amenity = st.selectbox("Özellik", ["Tümü"] + amenities)

    with col3:
        marina_types = ["commercial", "resort", "yacht_club", "private"]
        selected_type = st.selectbox("Marina Tipi", ["Tümü"] + marina_types)

    # Get filtered marinas
    marinas = database.get_all_marinas()

    if selected_country != "Tümü":
        marinas = [m for m in marinas if m.country == selected_country]

    if selected_type != "Tümü":
        marinas = [m for m in marinas if m.marina_type == selected_type]

    st.write(f"**{len(marinas)} marina bulundu**")

    # Display marinas
    for marina in marinas:
        with st.container():
            st.markdown(f"### {marina.name}")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Konum:** {marina.city}, {marina.country}")
                st.write(f"**Tip:** {marina.marina_type.title()}")
                st.write(f"**İletişim:** {marina.contact_email} | {marina.contact_phone}")

                if marina.website:
                    st.write(f"**Website:** {marina.website}")

                if marina.description:
                    st.write(f"*{marina.description}*")

                # Amenities
                st.write(f"**Özellikler:** {', '.join(marina.amenities[:5])}")

            with col2:
                st.metric("Toplam Yat Yeri", marina.total_berths)
                st.metric("Müsait", marina.available_berths)
                st.metric("Doluluk Oranı", f"{marina.occupancy_rate:.1f}%")

                if marina.max_boat_length_meters:
                    st.write(f"Max Tekne Boyu: {marina.max_boat_length_meters}m")

                if marina.certifications:
                    st.write(f"🏆 {', '.join(marina.certifications)}")

            st.markdown("---")


def show_booking_page():
    """Display booking page"""
    st.markdown('<div class="sub-header">⚓ Yat Yeri Rezervasyonu</div>', unsafe_allow_html=True)

    # Step 1: Select marina
    marinas = database.get_all_marinas()
    marina_options = {f"{m.name} - {m.city}, {m.country}": m.marina_id for m in marinas}

    selected_marina_name = st.selectbox("Marina Seçin", list(marina_options.keys()))
    selected_marina_id = marina_options[selected_marina_name]
    selected_marina = database.get_marina_by_id(selected_marina_id)

    st.markdown("---")

    # Step 2: Search criteria
    st.markdown("### 🔍 Arama Kriterleri")

    col1, col2 = st.columns(2)

    with col1:
        check_in = st.date_input("Giriş Tarihi", datetime.now())
        boat_length = st.number_input("Tekne Boyu (metre)", min_value=5.0, max_value=100.0, value=12.0, step=0.5)

    with col2:
        check_out = st.date_input("Çıkış Tarihi", datetime.now() + timedelta(days=7))
        needs_electricity = st.checkbox("Elektrik Gerekli", value=True)

    needs_water = st.checkbox("Su Gerekli", value=True)

    # Step 3: Search berths
    if st.button("🔍 Uygun Yat Yerlerini Ara", type="primary"):
        berths = database.search_available_berths(
            marina_id=selected_marina_id,
            min_length=boat_length,
            needs_electricity=needs_electricity,
            needs_water=needs_water
        )

        if not berths:
            st.warning("Üzgünüz, bu kriterlere uygun müsait yat yeri bulunamadı.")
        else:
            st.success(f"✅ {len(berths)} uygun yat yeri bulundu!")

            st.markdown("### Müsait Yat Yerleri")

            for berth in berths[:10]:  # Show first 10
                with st.expander(f"Yat Yeri {berth.number} - {berth.length_meters}m"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**Boy:** {berth.length_meters}m")
                        st.write(f"**En:** {berth.width_meters}m")
                        st.write(f"**Derinlik:** {berth.depth_meters}m")

                    with col2:
                        st.write(f"**Elektrik:** {'✅' if berth.has_electricity else '❌'}")
                        st.write(f"**Su:** {'✅' if berth.has_water else '❌'}")
                        st.write(f"**WiFi:** {'✅' if berth.has_wifi else '❌'}")

                    with col3:
                        nights = (check_out - check_in).days
                        total_price = berth.daily_rate * nights

                        st.write(f"**Günlük:** {format_currency(berth.daily_rate, berth.currency)}")
                        st.write(f"**{nights} Gece:** {format_currency(total_price, berth.currency)}")

                    # Booking form
                    with st.form(f"booking_form_{berth.berth_id}"):
                        customer_name = st.text_input("Müşteri Adı")
                        customer_email = st.text_input("E-posta")
                        customer_phone = st.text_input("Telefon")
                        boat_name = st.text_input("Tekne Adı")

                        services = st.multiselect(
                            "Ek Hizmetler",
                            ["Yakıt", "Su", "Elektrik", "Teknik Servis", "Çamaşırhane"]
                        )

                        submitted = st.form_submit_button("Rezervasyon Yap")

                        if submitted:
                            if not all([customer_name, customer_email, customer_phone, boat_name]):
                                st.error("Lütfen tüm alanları doldurun.")
                            else:
                                try:
                                    booking = database.create_booking(
                                        berth_id=berth.berth_id,
                                        customer_name=customer_name,
                                        customer_email=customer_email,
                                        customer_phone=customer_phone,
                                        boat_name=boat_name,
                                        boat_length=boat_length,
                                        check_in=check_in.isoformat(),
                                        check_out=check_out.isoformat(),
                                        services=services
                                    )

                                    st.success(f"✅ Rezervasyon başarılı! Rezervasyon No: {booking.booking_id}")
                                    st.balloons()

                                except Exception as e:
                                    st.error(f"Rezervasyon hatası: {str(e)}")


def show_analytics_page():
    """Display analytics and reports page"""
    st.markdown('<div class="sub-header">📊 Analitik ve Raporlar</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Doluluk Raporu", "💰 Gelir Raporu", "🌍 Bölgesel Genel Bakış"])

    with tab1:
        st.markdown("### Doluluk Raporu")

        if st.button("Rapor Oluştur", key="occupancy"):
            with st.spinner("Rapor hazırlanıyor..."):
                # Get occupancy report
                result = asyncio.run(
                    database.analytics_skill.execute("occupancy_report", {})
                )

                if result.get("success"):
                    st.success("✅ Rapor hazırlandı!")

                    # Overall stats
                    overall = result["overall_statistics"]
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Toplam Marina", overall["total_marinas"])
                    with col2:
                        st.metric("Toplam Yat Yeri", overall["total_berths"])
                    with col3:
                        st.metric("Dolu/Rezerve", overall["occupied_reserved"])
                    with col4:
                        st.metric("Doluluk Oranı", f"{overall['overall_occupancy_rate']:.1f}%")

                    st.markdown("---")

                    # Marina details
                    for marina_data in result["marina_data"]:
                        with st.expander(f"{marina_data['marina_name']} - {marina_data['location']}"):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write(f"**Toplam Yat Yeri:** {marina_data['total_berths']}")
                                st.write(f"**Müsait:** {marina_data['available']}")
                                st.write(f"**Dolu:** {marina_data['occupied']}")
                                st.write(f"**Rezerve:** {marina_data['reserved']}")

                            with col2:
                                st.write(f"**Bakımda:** {marina_data['maintenance']}")
                                st.write(f"**Doluluk Oranı:** {marina_data['occupancy_rate']:.1f}%")
                                st.write(f"**Durum:** {marina_data['occupancy_status']}")

    with tab2:
        st.markdown("### Gelir Raporu")

        target_currency = st.selectbox("Para Birimi", ["EUR", "USD", "TRY", "GBP"])

        if st.button("Rapor Oluştur", key="revenue"):
            with st.spinner("Rapor hazırlanıyor..."):
                # This would call the analytics skill
                st.info("Gelir raporu özelliği yakında eklenecek...")

    with tab3:
        st.markdown("### Bölgesel Genel Bakış")

        if st.button("Rapor Oluştur", key="regional"):
            with st.spinner("Rapor hazırlanıyor..."):
                # This would call the analytics skill
                st.info("Bölgesel rapor özelliği yakında eklenecek...")


def show_weather_page():
    """Display weather page"""
    st.markdown('<div class="sub-header">🌤️ Hava Durumu</div>', unsafe_allow_html=True)

    # Select marina
    marinas = database.get_all_marinas()
    marina_options = {f"{m.name} - {m.city}": m.marina_id for m in marinas}

    selected_marina_name = st.selectbox("Marina Seçin", list(marina_options.keys()))
    selected_marina_id = marina_options[selected_marina_name]

    if st.button("🌤️ Hava Durumunu Göster", type="primary"):
        with st.spinner("Hava durumu bilgisi alınıyor..."):
            # In production, this would call the weather skill
            st.info("Hava durumu özelliği yakında eklenecek...")


def show_maintenance_page():
    """Display maintenance page"""
    st.markdown('<div class="sub-header">🔧 Bakım Yönetimi</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📅 Bakım Planla", "📋 Bakım Kayıtları"])

    with tab1:
        st.markdown("### Yeni Bakım Görevi Planla")

        # Select marina
        marinas = database.get_all_marinas()
        marina_options = {f"{m.name}": m.marina_id for m in marinas}

        selected_marina_name = st.selectbox("Marina", list(marina_options.keys()))
        selected_marina_id = marina_options[selected_marina_name]

        description = st.text_area("Bakım Açıklaması")
        scheduled_date = st.date_input("Planlanan Tarih")
        estimated_cost = st.number_input("Tahmini Maliyet", min_value=0.0, value=100.0, step=10.0)

        if st.button("Bakım Planla", type="primary"):
            if description:
                st.success(f"✅ Bakım görevi {scheduled_date} tarihine planlandı!")
            else:
                st.error("Lütfen açıklama giriniz.")

    with tab2:
        st.markdown("### Bakım Kayıtları")
        st.info("Bakım kayıtları özelliği yakında eklenecek...")


def show_ai_assistant_page():
    """Display AI assistant page"""
    st.markdown('<div class="sub-header">💬 AI Asistan</div>', unsafe_allow_html=True)

    st.markdown("""
    Ada Maritime AI asistanı ile doğal dilde iletişim kurabilirsiniz.

    **Örnek Sorular:**
    - "Bodrum'da 15 metre tekneme uygun müsait yat yeri var mı?"
    - "Yunanistan'daki marinalarımızın doluluk oranı nedir?"
    - "Gelecek hafta bakım planlanmış işler neler?"
    - "En çok gelir getiren marinalarımız hangileri?"
    """)

    # Chat interface
    user_input = st.text_area("Sorunuzu yazın:", height=100)

    if st.button("🚀 Gönder", type="primary"):
        if user_input:
            with st.spinner("AI düşünüyor..."):
                # This would call the orchestrator
                st.info("AI asistan özelliği aktif olarak geliştirilmektedir...")
                st.write(f"**Siz:** {user_input}")
                st.write("**AI:** Bu özellik yakında aktif olacak!")
        else:
            st.warning("Lütfen bir soru yazın.")


if __name__ == "__main__":
    main()
