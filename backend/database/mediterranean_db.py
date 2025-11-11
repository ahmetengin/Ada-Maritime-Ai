"""Mediterranean Multi-Region Marina Database - Comprehensive Mock Implementation"""

import random
from typing import List, Optional
from datetime import datetime, timedelta

from .interface import DatabaseInterface
from .models import (
    Berth, Booking, Marina, OperatingHours, SeasonalPricing,
    Weather, MaintenanceRecord, Staff
)
from ..logger import setup_logger
from ..exceptions import (
    BerthNotFoundError,
    BerthNotAvailableError,
    BookingError
)


logger = setup_logger(__name__)


class MediterraneanDatabase(DatabaseInterface):
    """Comprehensive multi-region Mediterranean marina database"""

    def __init__(self) -> None:
        """Initialize mock data for Mediterranean marinas"""
        logger.info("Initializing Mediterranean Marina Database")

        self.marinas: List[Marina] = self._create_mediterranean_marinas()
        self.berths: List[Berth] = self._create_mock_berths()
        self.bookings: List[Booking] = []
        self.staff: List[Staff] = self._create_mock_staff()
        self.maintenance_records: List[MaintenanceRecord] = []

        logger.info(
            f"Database initialized: {len(self.marinas)} marinas across "
            f"{len(set(m.country for m in self.marinas))} countries, "
            f"{len(self.berths)} berths, {len(self.staff)} staff members"
        )

    def _create_mediterranean_marinas(self) -> List[Marina]:
        """Create comprehensive marina data for Turkey, Greece, and Mediterranean"""
        return [
            # ========== TURKEY - Turkish Marinas ==========
            Marina(
                marina_id="setur-bodrum-001",
                name="Setur Bodrum Marina",
                location="Neyzen Tevfik Caddesi, Bodrum",
                city="Bodrum",
                country="Turkey",
                country_code="TR",
                total_berths=450,
                available_berths=123,
                coordinates={"lat": 37.0349, "lon": 27.4305},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Technical Service", "Chandlery", "Shower/WC",
                    "Laundry", "Security 24/7", "Shopping Center"
                ],
                contact_email="bodrum@seturmarinas.com",
                contact_phone="+90 252 316 1860",
                currency="EUR",
                timezone="Europe/Istanbul",
                language="tr",
                marina_type="commercial",
                website="https://www.seturmarinas.com/bodrum",
                description="Premium marina in the heart of Bodrum, offering world-class facilities and services.",
                max_boat_length_meters=60.0,
                min_depth_meters=3.0,
                max_depth_meters=8.0,
                fuel_available=True,
                diesel_price_per_liter=1.45,
                gasoline_price_per_liter=1.65,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                supermarket=True,
                laundry=True,
                tax_rate=0.18,
                manager_name="Mehmet Yılmaz",
                founded_year=1998,
                certifications=["Blue Flag", "ISO 9001"],
                accepts_megayachts=True,
                has_travel_lift=True,
                travel_lift_capacity_tons=150.0
            ),
            Marina(
                marina_id="setur-kusadasi-001",
                name="Setur Kuşadası Marina",
                location="Atatürk Bulvarı, Kuşadası",
                city="Kuşadası",
                country="Turkey",
                country_code="TR",
                total_berths=580,
                available_berths=87,
                coordinates={"lat": 37.8607, "lon": 27.2615},
                amenities=[
                    "Restaurant", "Pool", "Spa", "Wifi",
                    "Fuel Station", "Repair Yard", "Shopping Center",
                    "Medical Service", "Fitness Center"
                ],
                contact_email="kusadasi@seturmarinas.com",
                contact_phone="+90 256 618 1150",
                currency="EUR",
                timezone="Europe/Istanbul",
                language="tr",
                marina_type="resort",
                website="https://www.seturmarinas.com/kusadasi",
                description="Full-service resort marina with spa and wellness facilities.",
                max_boat_length_meters=55.0,
                min_depth_meters=3.5,
                max_depth_meters=7.5,
                fuel_available=True,
                diesel_price_per_liter=1.42,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                supermarket=True,
                tax_rate=0.18,
                manager_name="Ayşe Demir",
                founded_year=2005,
                certifications=["Blue Flag", "Clean Marina"],
                accepts_megayachts=True,
                has_travel_lift=True,
                travel_lift_capacity_tons=120.0
            ),
            Marina(
                marina_id="setur-cesme-001",
                name="Setur Çeşme Marina",
                location="Çeşme Limanı, Çeşme",
                city="Çeşme",
                country="Turkey",
                country_code="TR",
                total_berths=380,
                available_berths=145,
                coordinates={"lat": 38.3190, "lon": 26.3020},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Technical Service", "Sailing School", "Beach Club"
                ],
                contact_email="cesme@seturmarinas.com",
                contact_phone="+90 232 723 1250",
                currency="EUR",
                timezone="Europe/Istanbul",
                language="tr",
                marina_type="commercial",
                website="https://www.seturmarinas.com/cesme",
                description="Popular marina with sailing school and beach club access.",
                max_boat_length_meters=45.0,
                min_depth_meters=2.5,
                max_depth_meters=6.0,
                fuel_available=True,
                diesel_price_per_liter=1.40,
                security_24h=True,
                repair_services=True,
                restaurant=True,
                tax_rate=0.18,
                manager_name="Can Özdemir",
                founded_year=2000,
                certifications=["Blue Flag"],
                has_travel_lift=True,
                travel_lift_capacity_tons=80.0
            ),
            Marina(
                marina_id="istanbul-kalamis-001",
                name="Kalamış Marina",
                location="Fenerbahçe, Kadıköy",
                city="Istanbul",
                country="Turkey",
                country_code="TR",
                total_berths=720,
                available_berths=98,
                coordinates={"lat": 40.9732, "lon": 29.0264},
                amenities=[
                    "Restaurant", "Cafe", "Wifi", "Fuel Station",
                    "Yacht Club", "Shopping Mall", "Parking",
                    "Security 24/7", "Medical Service"
                ],
                contact_email="info@kalamisyat.com.tr",
                contact_phone="+90 216 345 6789",
                currency="TRY",
                timezone="Europe/Istanbul",
                language="tr",
                marina_type="yacht_club",
                website="https://www.kalamisyat.com.tr",
                description="Istanbul's premier yacht club and marina facility on the Asian side.",
                max_boat_length_meters=50.0,
                min_depth_meters=3.0,
                max_depth_meters=7.0,
                fuel_available=True,
                diesel_price_per_liter=1.48,
                security_24h=True,
                customs_available=False,
                repair_services=True,
                restaurant=True,
                supermarket=True,
                tax_rate=0.18,
                manager_name="Serkan Aydın",
                founded_year=1996,
                certifications=["ISO 9001", "Clean Marina"],
                has_travel_lift=True,
                travel_lift_capacity_tons=100.0
            ),
            Marina(
                marina_id="marmaris-netsel-001",
                name="Netsel Marmaris Marina",
                location="Marmaris Yat Limanı",
                city="Marmaris",
                country="Turkey",
                country_code="TR",
                total_berths=750,
                available_berths=156,
                coordinates={"lat": 36.8513, "lon": 28.2708},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Repair Yard", "Chandlery", "Car Rental",
                    "Shopping Center", "Medical Service"
                ],
                contact_email="info@netsel.com.tr",
                contact_phone="+90 252 412 2708",
                currency="EUR",
                timezone="Europe/Istanbul",
                language="tr",
                marina_type="commercial",
                website="https://www.netsel.com.tr",
                description="One of Turkey's largest and most equipped marinas.",
                max_boat_length_meters=70.0,
                min_depth_meters=4.0,
                max_depth_meters=10.0,
                fuel_available=True,
                diesel_price_per_liter=1.43,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                supermarket=True,
                tax_rate=0.18,
                manager_name="Erkan Kaya",
                founded_year=1990,
                certifications=["Blue Flag", "ISO 9001", "TYHA Gold Anchor"],
                accepts_megayachts=True,
                has_travel_lift=True,
                travel_lift_capacity_tons=200.0
            ),

            # ========== GREECE - Greek Marinas ==========
            Marina(
                marina_id="athens-alimos-001",
                name="Alimos Marina (Athens Marina)",
                location="Kalamaki, Alimos",
                city="Athens",
                country="Greece",
                country_code="GR",
                total_berths=1100,
                available_berths=234,
                coordinates={"lat": 37.9140, "lon": 23.7141},
                amenities=[
                    "Restaurant", "Bar", "Cafe", "Wifi",
                    "Fuel Station", "Repair Services", "Chandlery",
                    "Shopping", "Parking", "Security 24/7"
                ],
                contact_email="info@alimos-marina.gr",
                contact_phone="+30 210 988 8000",
                currency="EUR",
                timezone="Europe/Athens",
                language="el",
                marina_type="commercial",
                website="https://www.alimos-marina.gr",
                description="Greece's largest marina, located in the heart of Athens Riviera.",
                max_boat_length_meters=80.0,
                min_depth_meters=4.0,
                max_depth_meters=12.0,
                fuel_available=True,
                diesel_price_per_liter=1.38,
                gasoline_price_per_liter=1.58,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                supermarket=True,
                tax_rate=0.24,
                manager_name="Dimitris Papadopoulos",
                founded_year=2004,
                certifications=["Blue Flag", "ISO 14001", "ISO 9001"],
                accepts_megayachts=True,
                has_travel_lift=True,
                travel_lift_capacity_tons=250.0
            ),
            Marina(
                marina_id="athens-flisvos-001",
                name="Flisvos Marina",
                location="Paleo Faliro",
                city="Athens",
                country="Greece",
                country_code="GR",
                total_berths=303,
                available_berths=67,
                coordinates={"lat": 37.9323, "lon": 23.6927},
                amenities=[
                    "Restaurant", "Bar", "Cafe", "Wifi",
                    "Shopping Mall", "Cinema", "Parking",
                    "Security 24/7", "Kids Playground"
                ],
                contact_email="marina@flisvos.gr",
                contact_phone="+30 210 987 7000",
                currency="EUR",
                timezone="Europe/Athens",
                language="el",
                marina_type="resort",
                website="https://www.flisvosmarina.com",
                description="Premium lifestyle marina with shopping and entertainment complex.",
                max_boat_length_meters=65.0,
                min_depth_meters=3.5,
                max_depth_meters=8.0,
                fuel_available=True,
                diesel_price_per_liter=1.40,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                supermarket=True,
                tax_rate=0.24,
                manager_name="Nikos Andriopoulos",
                founded_year=2006,
                certifications=["Blue Flag", "Clean Marina"],
                accepts_megayachts=True,
                has_travel_lift=False
            ),
            Marina(
                marina_id="corfu-gouvia-001",
                name="Gouvia Marina",
                location="Gouvia Bay",
                city="Corfu",
                country="Greece",
                country_code="GR",
                total_berths=1235,
                available_berths=289,
                coordinates={"lat": 39.6458, "lon": 19.8467},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Repair Yard", "Chandlery", "Laundry",
                    "Swimming Pool", "Mini Market"
                ],
                contact_email="info@gouviamarina.gr",
                contact_phone="+30 26610 91900",
                currency="EUR",
                timezone="Europe/Athens",
                language="el",
                marina_type="commercial",
                website="https://www.gouviamarina.gr",
                description="Major Ionian Sea marina, ideal base for exploring Greek islands.",
                max_boat_length_meters=60.0,
                min_depth_meters=3.0,
                max_depth_meters=9.0,
                fuel_available=True,
                diesel_price_per_liter=1.36,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                supermarket=True,
                tax_rate=0.24,
                manager_name="Yannis Konstantinou",
                founded_year=1999,
                certifications=["Blue Flag"],
                accepts_megayachts=True,
                has_travel_lift=True,
                travel_lift_capacity_tons=180.0
            ),
            Marina(
                marina_id="rhodes-mandraki-001",
                name="Mandraki Marina Rhodes",
                location="Mandraki Harbor",
                city="Rhodes",
                country="Greece",
                country_code="GR",
                total_berths=250,
                available_berths=45,
                coordinates={"lat": 36.4496, "lon": 28.2263},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Chandlery", "Old Town Access", "Historical Sites"
                ],
                contact_email="info@rhodesmarina.gr",
                contact_phone="+30 22410 27690",
                currency="EUR",
                timezone="Europe/Athens",
                language="el",
                marina_type="municipal",
                website="https://www.rhodesmarina.gr",
                description="Historic marina in Rhodes Old Town, UNESCO World Heritage site.",
                max_boat_length_meters=50.0,
                min_depth_meters=3.0,
                max_depth_meters=7.0,
                fuel_available=True,
                diesel_price_per_liter=1.42,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                tax_rate=0.24,
                manager_name="Kostas Mavridis",
                founded_year=1988,
                certifications=["UNESCO Heritage Marina"],
                has_travel_lift=False
            ),
            Marina(
                marina_id="mykonos-ornos-001",
                name="Ornos Bay Marina",
                location="Ornos Beach",
                city="Mykonos",
                country="Greece",
                country_code="GR",
                total_berths=180,
                available_berths=28,
                coordinates={"lat": 37.4305, "lon": 25.3367},
                amenities=[
                    "Restaurant", "Beach Club", "Wifi", "Fuel",
                    "Luxury Services", "VIP Concierge", "Water Sports"
                ],
                contact_email="info@ornosmarina.gr",
                contact_phone="+30 22890 23700",
                currency="EUR",
                timezone="Europe/Athens",
                language="el",
                marina_type="private",
                website="https://www.mykonosmarina.gr",
                description="Exclusive boutique marina in cosmopolitan Mykonos.",
                max_boat_length_meters=55.0,
                min_depth_meters=4.0,
                max_depth_meters=10.0,
                fuel_available=True,
                diesel_price_per_liter=1.55,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                supermarket=False,
                tax_rate=0.24,
                manager_name="Elena Papadaki",
                founded_year=2010,
                certifications=["Blue Flag", "Luxury Marina Award"],
                accepts_megayachts=True,
                has_travel_lift=False
            ),
            Marina(
                marina_id="santorini-vlychada-001",
                name="Vlychada Marina",
                location="Vlychada Beach",
                city="Santorini",
                country="Greece",
                country_code="GR",
                total_berths=116,
                available_berths=34,
                coordinates={"lat": 36.3555, "lon": 25.4340},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Caldera Views", "Sunset Terrace", "Wine Tours"
                ],
                contact_email="info@santorinimarina.gr",
                contact_phone="+30 22860 82239",
                currency="EUR",
                timezone="Europe/Athens",
                language="el",
                marina_type="commercial",
                website="https://www.santorinimarina.gr",
                description="Picturesque marina with stunning caldera views.",
                max_boat_length_meters=40.0,
                min_depth_meters=5.0,
                max_depth_meters=15.0,
                fuel_available=True,
                diesel_price_per_liter=1.50,
                security_24h=True,
                customs_available=True,
                repair_services=False,
                restaurant=True,
                tax_rate=0.24,
                manager_name="Stavros Dimitriou",
                founded_year=2012,
                certifications=["Blue Flag"],
                has_travel_lift=False
            ),

            # ========== CROATIA - Croatian Marinas ==========
            Marina(
                marina_id="dubrovnik-aci-001",
                name="ACI Marina Dubrovnik",
                location="Komolac",
                city="Dubrovnik",
                country="Croatia",
                country_code="HR",
                total_berths=380,
                available_berths=78,
                coordinates={"lat": 42.6629, "lon": 18.0864},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Swimming Pool", "Repair Services", "Chandlery"
                ],
                contact_email="m.dubrovnik@aci-club.hr",
                contact_phone="+385 20 455 020",
                currency="EUR",
                timezone="Europe/Zagreb",
                language="hr",
                marina_type="commercial",
                website="https://www.aci-club.hr/dubrovnik",
                description="Modern marina near UNESCO-protected Dubrovnik Old City.",
                max_boat_length_meters=60.0,
                min_depth_meters=3.0,
                max_depth_meters=10.0,
                fuel_available=True,
                diesel_price_per_liter=1.35,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                supermarket=True,
                tax_rate=0.25,
                manager_name="Ivan Kovač",
                founded_year=2001,
                certifications=["Blue Flag", "ISO 9001"],
                accepts_megayachts=True,
                has_travel_lift=True,
                travel_lift_capacity_tons=160.0
            ),

            # ========== ITALY - Italian Marinas ==========
            Marina(
                marina_id="porto-cervo-001",
                name="Marina di Porto Cervo",
                location="Costa Smeralda",
                city="Porto Cervo",
                country="Italy",
                country_code="IT",
                total_berths=700,
                available_berths=89,
                coordinates={"lat": 41.1384, "lon": 9.5348},
                amenities=[
                    "Restaurant", "Bar", "Luxury Shopping", "Wifi",
                    "Fuel Station", "Concierge", "Helipad", "Spa"
                ],
                contact_email="info@marinadiportocervo.com",
                contact_phone="+39 0789 92661",
                currency="EUR",
                timezone="Europe/Rome",
                language="it",
                marina_type="private",
                website="https://www.marinadiportocervo.com",
                description="World-renowned luxury marina on Sardinia's Costa Smeralda.",
                max_boat_length_meters=180.0,
                min_depth_meters=5.0,
                max_depth_meters=20.0,
                fuel_available=True,
                diesel_price_per_liter=1.65,
                gasoline_price_per_liter=1.85,
                security_24h=True,
                customs_available=True,
                repair_services=True,
                restaurant=True,
                supermarket=True,
                tax_rate=0.22,
                manager_name="Marco Rossi",
                founded_year=1962,
                certifications=["Luxury Marina", "MYBA", "ISO 9001"],
                accepts_megayachts=True,
                has_travel_lift=True,
                travel_lift_capacity_tons=500.0
            ),
        ]

    def _create_mock_berths(self) -> List[Berth]:
        """Create comprehensive berth data for all marinas"""
        berths: List[Berth] = []
        sections = ["A", "B", "C", "D", "E"]
        statuses = ["available", "occupied", "reserved", "maintenance"]

        for marina in self.marinas:
            berths_per_section = marina.total_berths // len(sections)

            for section in sections:
                for num in range(1, berths_per_section + 1):
                    # Vary berth sizes and pricing based on marina and size
                    if num % 5 == 0:  # Mega yacht berths
                        length = random.uniform(25.0, 40.0)
                        width = random.uniform(8.0, 12.0)
                        base_rate = random.uniform(300, 600)
                        berth_type = "mega_yacht"
                        has_fuel = True
                        shore_power = 125
                    elif num % 3 == 0:  # Large berths
                        length = random.uniform(18.0, 25.0)
                        width = random.uniform(6.0, 8.0)
                        base_rate = random.uniform(180, 300)
                        berth_type = "premium"
                        has_fuel = True
                        shore_power = 63
                    elif num % 3 == 1:  # Medium berths
                        length = random.uniform(12.0, 18.0)
                        width = random.uniform(4.0, 6.0)
                        base_rate = random.uniform(120, 180)
                        berth_type = "standard"
                        has_fuel = False
                        shore_power = 32
                    else:  # Small berths
                        length = random.uniform(8.0, 12.0)
                        width = random.uniform(3.0, 4.0)
                        base_rate = random.uniform(80, 120)
                        berth_type = "standard"
                        has_fuel = False
                        shore_power = 16

                    # Adjust pricing based on marina country and type
                    if marina.country == "Greece":
                        daily_rate = base_rate * 0.95
                    elif marina.country == "Croatia":
                        daily_rate = base_rate * 0.85
                    elif marina.country == "Italy" and "Porto Cervo" in marina.name:
                        daily_rate = base_rate * 2.0
                    else:
                        daily_rate = base_rate

                    berth = Berth(
                        berth_id=f"{marina.marina_id}-{section}{num:03d}",
                        marina_id=marina.marina_id,
                        section=section,
                        number=f"{section}{num:03d}",
                        length_meters=round(length, 1),
                        width_meters=round(width, 1),
                        depth_meters=round(random.uniform(marina.min_depth_meters, marina.max_depth_meters), 1),
                        has_electricity=(num % 4 != 0),
                        has_water=(num % 3 != 0),
                        has_wifi=True,
                        daily_rate=round(daily_rate, 2),
                        currency=marina.currency,
                        status=random.choice(statuses) if random.random() < 0.3 else "available",
                        current_boat_name=f"Vessel-{random.randint(1000, 9999)}" if random.random() < 0.2 else None,
                        berth_type=berth_type,
                        max_beam_meters=width,
                        has_fuel=has_fuel,
                        has_pump_out=(num % 2 == 0),
                        has_shore_power_amps=shore_power,
                    )
                    berths.append(berth)

        logger.info(f"Created {len(berths)} berths across all marinas")
        return berths

    def _create_mock_staff(self) -> List[Staff]:
        """Create mock staff for all marinas"""
        staff_members = []
        roles = ["manager", "dock_master", "maintenance", "security", "customer_service"]

        for marina in self.marinas:
            # Create 3-5 staff members per marina
            for i in range(random.randint(3, 5)):
                role = random.choice(roles)
                staff = Staff(
                    staff_id=f"STAFF-{marina.marina_id}-{i:02d}",
                    marina_id=marina.marina_id,
                    name=f"Staff Member {i+1}",
                    role=role,
                    email=f"staff{i+1}@{marina.marina_id}.com",
                    phone=marina.contact_phone,
                    shift_start="08:00",
                    shift_end="18:00",
                    is_active=True
                )
                staff_members.append(staff)

        return staff_members

    def get_marina_by_id(self, marina_id: str) -> Optional[Marina]:
        """Get marina by ID"""
        marina = next(
            (m for m in self.marinas if m.marina_id == marina_id),
            None
        )

        if marina:
            logger.debug(f"Found marina: {marina.name}")
        else:
            logger.warning(f"Marina not found: {marina_id}")

        return marina

    def get_all_marinas(self) -> List[Marina]:
        """Get all marinas"""
        logger.debug(f"Returning {len(self.marinas)} marinas")
        return self.marinas

    def get_marinas_by_country(self, country_code: str) -> List[Marina]:
        """Get all marinas in a specific country"""
        marinas = [m for m in self.marinas if m.country_code == country_code]
        logger.debug(f"Found {len(marinas)} marinas in {country_code}")
        return marinas

    def search_available_berths(
        self,
        marina_id: Optional[str] = None,
        min_length: Optional[float] = None,
        max_length: Optional[float] = None,
        check_in: Optional[str] = None,
        check_out: Optional[str] = None,
        needs_electricity: bool = False,
        needs_water: bool = False
    ) -> List[Berth]:
        """Search for available berths with filters"""

        logger.info(
            f"Searching berths: marina={marina_id}, "
            f"length={min_length}-{max_length}, "
            f"electricity={needs_electricity}, water={needs_water}"
        )

        results = [b for b in self.berths if b.is_available()]

        if marina_id:
            results = [b for b in results if b.marina_id == marina_id]

        if min_length:
            results = [b for b in results if b.length_meters >= min_length]

        if max_length:
            results = [b for b in results if b.length_meters <= max_length]

        if needs_electricity:
            results = [b for b in results if b.has_electricity]

        if needs_water:
            results = [b for b in results if b.has_water]

        # Sort by price
        results.sort(key=lambda b: b.daily_rate)

        logger.info(f"Found {len(results)} available berths")

        return results

    def get_berth_by_id(self, berth_id: str) -> Optional[Berth]:
        """Get berth by ID"""
        berth = next(
            (b for b in self.berths if b.berth_id == berth_id),
            None
        )

        if berth:
            logger.debug(f"Found berth: {berth.number}")
        else:
            logger.warning(f"Berth not found: {berth_id}")

        return berth

    def create_booking(
        self,
        berth_id: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        boat_name: str,
        boat_length: float,
        check_in: str,
        check_out: str,
        services: List[str]
    ) -> Booking:
        """Create a new booking"""

        logger.info(f"Creating booking for berth: {berth_id}")

        berth = self.get_berth_by_id(berth_id)
        if not berth:
            raise BerthNotFoundError(f"Berth {berth_id} not found")

        if not berth.is_available():
            raise BerthNotAvailableError(
                f"Berth {berth_id} is {berth.status}"
            )

        if not berth.is_suitable_for_boat(boat_length):
            raise BookingError(
                f"Berth {berth_id} ({berth.length_meters}m) too small "
                f"for boat ({boat_length}m)"
            )

        try:
            check_in_dt = datetime.fromisoformat(check_in)
            check_out_dt = datetime.fromisoformat(check_out)
            nights = (check_out_dt - check_in_dt).days

            if nights <= 0:
                raise BookingError("Check-out must be after check-in")

        except ValueError as e:
            raise BookingError(f"Invalid date format: {e}")

        total_price = berth.daily_rate * nights

        booking_id = f"BK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        booking = Booking(
            booking_id=booking_id,
            berth_id=berth_id,
            marina_id=berth.marina_id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            boat_name=boat_name,
            boat_length_meters=boat_length,
            check_in=check_in,
            check_out=check_out,
            total_nights=nights,
            total_price=round(total_price, 2),
            currency=berth.currency,
            status="confirmed",
            created_at=datetime.now().isoformat(),
            services_requested=services
        )

        self.bookings.append(booking)

        # Update berth status
        berth.status = "reserved"
        berth.current_booking_id = booking_id
        berth.current_boat_name = boat_name

        logger.info(
            f"Booking created: {booking_id} for {nights} nights, "
            f"{berth.currency} {total_price:.2f}"
        )

        return booking

    def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        booking = next(
            (b for b in self.bookings if b.booking_id == booking_id),
            None
        )

        if booking:
            logger.debug(f"Found booking: {booking_id}")
        else:
            logger.warning(f"Booking not found: {booking_id}")

        return booking

    def get_bookings_by_marina(self, marina_id: str) -> List[Booking]:
        """Get all bookings for a marina"""
        bookings = [b for b in self.bookings if b.marina_id == marina_id]
        logger.debug(f"Found {len(bookings)} bookings for marina: {marina_id}")
        return bookings

    def get_all_berths(self) -> List[Berth]:
        """Get all berths"""
        logger.debug(f"Returning {len(self.berths)} berths")
        return self.berths


# Singleton instance
_db_instance: Optional[MediterraneanDatabase] = None


def get_mediterranean_database() -> MediterraneanDatabase:
    """Get or create global Mediterranean database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = MediterraneanDatabase()
    return _db_instance
