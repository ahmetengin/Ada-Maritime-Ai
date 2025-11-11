"""Mock Setur Marina Database - Refactored"""

import random
from typing import List, Optional
from datetime import datetime, timedelta

from .interface import DatabaseInterface
from .models import Berth, Booking, Marina
from ..logger import setup_logger
from ..exceptions import (
    BerthNotFoundError,
    BerthNotAvailableError,
    BookingError
)


logger = setup_logger(__name__)


class SeturMockDatabase(DatabaseInterface):
    """Mock database for Setur Marina operations"""

    def __init__(self) -> None:
        """Initialize mock data"""
        logger.info("Initializing Setur Mock Database")
        
        self.marinas: List[Marina] = self._create_mock_marinas()
        self.berths: List[Berth] = self._create_mock_berths()
        self.bookings: List[Booking] = []
        
        logger.info(
            f"Database initialized: {len(self.marinas)} marinas, "
            f"{len(self.berths)} berths"
        )

    def _create_mock_marinas(self) -> List[Marina]:
        """Create mock marina data"""
        return [
            # ============ SETUR MARINAS ============
            Marina(
                marina_id="setur-bodrum-001",
                name="Setur Bodrum Marina",
                location="Bodrum, Muğla",
                country="Turkey",
                total_berths=450,
                available_berths=123,
                coordinates={"lat": 37.0349, "lon": 27.4305},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Technical Service", "Chandlery", "Shower/WC",
                    "Laundry", "Security 24/7"
                ],
                contact_email="bodrum@seturmarinas.com",
                contact_phone="+90 252 316 1860"
            ),
            Marina(
                marina_id="setur-kusadasi-001",
                name="Setur Kuşadası Marina",
                location="Kuşadası, Aydın",
                country="Turkey",
                total_berths=580,
                available_berths=87,
                coordinates={"lat": 37.8607, "lon": 27.2615},
                amenities=[
                    "Restaurant", "Pool", "Spa", "Wifi",
                    "Fuel Station", "Repair Yard", "Shopping Center",
                    "Medical Service"
                ],
                contact_email="kusadasi@seturmarinas.com",
                contact_phone="+90 256 618 1150"
            ),
            Marina(
                marina_id="setur-cesme-001",
                name="Setur Çeşme Marina",
                location="Çeşme, İzmir",
                country="Turkey",
                total_berths=380,
                available_berths=145,
                coordinates={"lat": 38.3190, "lon": 26.3020},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Technical Service", "Sailing School"
                ],
                contact_email="cesme@seturmarinas.com",
                contact_phone="+90 232 723 1250"
            ),
            Marina(
                marina_id="setur-antalya-001",
                name="Setur Antalya Marina",
                location="Antalya",
                country="Turkey",
                total_berths=235,
                available_berths=67,
                coordinates={"lat": 36.8348, "lon": 30.6148},
                amenities=[
                    "Restaurant", "Wifi", "Fuel Station",
                    "Travel Lift 200T", "Technical Service", "Dry Storage",
                    "Shower/WC", "Security 24/7"
                ],
                contact_email="antalya@seturmarinas.com",
                contact_phone="+90 242 259 1190"
            ),
            Marina(
                marina_id="setur-kas-001",
                name="Setur Kaş Marina",
                location="Kaş, Antalya",
                country="Turkey",
                total_berths=472,
                available_berths=142,
                coordinates={"lat": 36.2086, "lon": 29.6153},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Technical Service", "Chandlery", "Dry Storage",
                    "Shopping", "Medical Service"
                ],
                contact_email="kas@seturmarinas.com",
                contact_phone="+90 242 836 1710"
            ),
            Marina(
                marina_id="setur-marmaris-001",
                name="Netsel Setur Marmaris Marina",
                location="Marmaris, Muğla",
                country="Turkey",
                total_berths=830,
                available_berths=234,
                coordinates={"lat": 36.8507, "lon": 28.2772},
                amenities=[
                    "Restaurant", "Bar", "Pool", "Spa", "Wifi",
                    "Fuel Station", "Repair Yard", "Chandlery",
                    "Shopping Center", "Medical Service", "Laundry",
                    "Security 24/7"
                ],
                contact_email="marmaris@seturmarinas.com",
                contact_phone="+90 252 412 2708"
            ),
            Marina(
                marina_id="setur-finike-001",
                name="Setur Finike Marina",
                location="Finike, Antalya",
                country="Turkey",
                total_berths=320,
                available_berths=89,
                coordinates={"lat": 36.2947, "lon": 30.1526},
                amenities=[
                    "Restaurant", "Wifi", "Fuel Station",
                    "Technical Service", "Dry Storage", "Shower/WC",
                    "Security 24/7"
                ],
                contact_email="finike@seturmarinas.com",
                contact_phone="+90 242 855 5003"
            ),
            Marina(
                marina_id="setur-ayvalik-001",
                name="Setur Ayvalık Marina",
                location="Ayvalık, Balıkesir",
                country="Turkey",
                total_berths=200,
                available_berths=54,
                coordinates={"lat": 39.3140, "lon": 26.6880},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Technical Service", "Dry Storage", "Shower/WC",
                    "Laundry"
                ],
                contact_email="ayvalik@seturmarinas.com",
                contact_phone="+90 266 312 1545"
            ),
            Marina(
                marina_id="setur-yalova-001",
                name="Setur Yalova Marina",
                location="Yalova",
                country="Turkey",
                total_berths=240,
                available_berths=71,
                coordinates={"lat": 40.6614, "lon": 29.2745},
                amenities=[
                    "Restaurant", "Wifi", "Fuel Station",
                    "Technical Service", "Dry Storage", "Shower/WC",
                    "Security 24/7"
                ],
                contact_email="yalova@seturmarinas.com",
                contact_phone="+90 226 814 4848"
            ),

            # ============ D-MARIN MARINAS ============
            Marina(
                marina_id="dmarin-turgutreis-001",
                name="D-Marin Turgutreis",
                location="Turgutreis, Bodrum, Muğla",
                country="Turkey",
                total_berths=532,
                available_berths=158,
                coordinates={"lat": 36.9992, "lon": 27.2553},
                amenities=[
                    "Restaurant", "Bar", "Pool", "Spa", "Wifi",
                    "Fuel Station", "Travel Lift", "Technical Service",
                    "Chandlery", "Shopping Center", "Medical Service",
                    "Dry Storage", "Security 24/7"
                ],
                contact_email="turgutreis@d-marin.com",
                contact_phone="+90 252 382 8600"
            ),
            Marina(
                marina_id="dmarin-didim-001",
                name="D-Marin Didim",
                location="Didim, Aydın",
                country="Turkey",
                total_berths=576,
                available_berths=172,
                coordinates={"lat": 37.3406, "lon": 27.2594},
                amenities=[
                    "Restaurant", "Bar", "Wifi", "Fuel Station",
                    "Travel Lift 400T", "Technical Service", "Chandlery",
                    "Superyacht Services", "Dry Storage", "Catamaran Center",
                    "Shopping", "Security 24/7"
                ],
                contact_email="didim@d-marin.com",
                contact_phone="+90 256 811 1100"
            ),
            Marina(
                marina_id="dmarin-gocek-001",
                name="D-Marin Göcek",
                location="Göcek, Fethiye, Muğla",
                country="Turkey",
                total_berths=380,
                available_berths=114,
                coordinates={"lat": 36.7483, "lon": 28.9433},
                amenities=[
                    "Restaurant", "Bar", "Beach Club", "Wifi",
                    "Fuel Station", "Technical Service", "Chandlery",
                    "Shopping", "Medical Service", "Dry Storage",
                    "National Park Access", "Security 24/7"
                ],
                contact_email="gocek@d-marin.com",
                contact_phone="+90 252 645 2760"
            )
        ]

    def _create_mock_berths(self) -> List[Berth]:
        """Create mock berth data"""
        berths: List[Berth] = []
        sections = ["A", "B", "C", "D", "E"]
        statuses = ["available", "occupied", "reserved"]

        for marina in self.marinas:
            berths_per_section = marina.total_berths // len(sections)

            for section in sections:
                for num in range(1, berths_per_section + 1):
                    # Vary berth sizes
                    if num % 3 == 0:
                        length = random.uniform(18.0, 25.0)
                        daily_rate = random.uniform(180, 300)
                    elif num % 3 == 1:
                        length = random.uniform(12.0, 18.0)
                        daily_rate = random.uniform(120, 180)
                    else:
                        length = random.uniform(8.0, 12.0)
                        daily_rate = random.uniform(80, 120)

                    berth = Berth(
                        berth_id=f"{marina.marina_id}-{section}{num:02d}",
                        marina_id=marina.marina_id,
                        section=section,
                        number=f"{section}{num:02d}",
                        length_meters=round(length, 1),
                        width_meters=round(length * 0.3, 1),
                        depth_meters=round(random.uniform(2.5, 5.0), 1),
                        has_electricity=(num % 4 != 0),
                        has_water=(num % 3 != 0),
                        has_wifi=True,
                        daily_rate_eur=round(daily_rate, 2),
                        status=random.choice(statuses),
                        current_boat_name=f"Boat-{num}" if random.random() < 0.3 else None
                    )
                    berths.append(berth)

        return berths

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
        results.sort(key=lambda b: b.daily_rate_eur)
        
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

        total_price = berth.daily_rate_eur * nights

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
            total_price_eur=round(total_price, 2),
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
            f"€{total_price:.2f}"
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
_db_instance: Optional[SeturMockDatabase] = None


def get_database() -> SeturMockDatabase:
    """Get or create global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SeturMockDatabase()
    return _db_instance
