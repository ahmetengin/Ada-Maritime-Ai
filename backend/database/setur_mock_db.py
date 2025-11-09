"""Mock Setur Marina Database - POC"""

import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import random


@dataclass
class Berth:
    berth_id: str
    marina_id: str
    section: str
    number: str
    length_meters: float
    width_meters: float
    depth_meters: float
    has_electricity: bool
    has_water: bool
    has_wifi: bool
    daily_rate_eur: float
    status: str
    current_boat_name: Optional[str] = None
    current_booking_id: Optional[str] = None


@dataclass
class Booking:
    booking_id: str
    berth_id: str
    marina_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    boat_name: str
    boat_length_meters: float
    check_in: str
    check_out: str
    total_nights: int
    total_price_eur: float
    status: str
    created_at: str
    services_requested: List[str]


@dataclass
class Marina:
    marina_id: str
    name: str
    location: str
    country: str
    total_berths: int
    available_berths: int
    coordinates: Dict[str, float]
    amenities: List[str]
    contact_email: str
    contact_phone: str


class SeturMockDatabase:
    """Mock database for Setur Marina operations"""

    def __init__(self):
        self.marinas = self._create_mock_marinas()
        self.berths = self._create_mock_berths()
        self.bookings = self._create_mock_bookings()

    def _create_mock_marinas(self) -> List[Marina]:
        return [
            Marina(
                marina_id="setur-bodrum-001",
                name="Setur Bodrum Marina",
                location="Bodrum, Muğla",
                country="Turkey",
                total_berths=450,
                available_berths=123,
                coordinates={"lat": 37.0349, "lon": 27.4305},
                amenities=["Restaurant", "Bar", "Wifi", "Fuel Station", "Technical Service"],
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
                amenities=["Restaurant", "Pool", "Spa", "Wifi", "Fuel Station"],
                contact_email="kusadasi@seturmarinas.com",
                contact_phone="+90 256 618 1150"
            )
        ]

    def _create_mock_berths(self) -> List[Berth]:
        berths = []
        sections = ["A", "B", "C", "D"]
        statuses = ["available", "occupied", "reserved"]

        for marina in self.marinas:
            berths_per_section = marina.total_berths // len(sections)

            for section in sections:
                for num in range(1, berths_per_section + 1):
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

    def _create_mock_bookings(self) -> List[Booking]:
        return []

    def get_marina_by_id(self, marina_id: str) -> Optional[Marina]:
        return next((m for m in self.marinas if m.marina_id == marina_id), None)

    def get_all_marinas(self) -> List[Marina]:
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
        results = [b for b in self.berths if b.status == "available"]

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

        results.sort(key=lambda b: b.daily_rate_eur)
        return results

    def get_berth_by_id(self, berth_id: str) -> Optional[Berth]:
        return next((b for b in self.berths if b.berth_id == berth_id), None)

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
        berth = self.get_berth_by_id(berth_id)
        if not berth:
            raise ValueError(f"Berth {berth_id} not found")

        if berth.status != "available":
            raise ValueError(f"Berth {berth_id} is not available")

        check_in_dt = datetime.fromisoformat(check_in)
        check_out_dt = datetime.fromisoformat(check_out)
        nights = (check_out_dt - check_in_dt).days
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
        berth.status = "reserved"
        berth.current_booking_id = booking_id
        berth.current_boat_name = boat_name

        return booking

    def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        return next((b for b in self.bookings if b.booking_id == booking_id), None)


_db_instance: Optional[SeturMockDatabase] = None


def get_database() -> SeturMockDatabase:
    global _db_instance
    if _db_instance is None:
        _db_instance = SeturMockDatabase()
    return _db_instance
