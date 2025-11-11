"""Data models for Ada Maritime AI - Multi-region marina management system"""

from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum


class Currency(Enum):
    """Supported currencies"""
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    TRY = "TRY"
    CHF = "CHF"


class MarinaType(Enum):
    """Marina types"""
    COMMERCIAL = "commercial"
    YACHT_CLUB = "yacht_club"
    MUNICIPAL = "municipal"
    PRIVATE = "private"
    RESORT = "resort"


class MaintenanceStatus(Enum):
    """Maintenance status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class OperatingHours:
    """Operating hours for marina services"""
    day_of_week: str  # "monday", "tuesday", etc.
    open_time: str  # "08:00"
    close_time: str  # "20:00"
    is_closed: bool = False


@dataclass
class SeasonalPricing:
    """Seasonal pricing configuration"""
    season_name: str
    start_date: str  # "MM-DD" format
    end_date: str  # "MM-DD" format
    price_multiplier: float  # 1.0 = normal, 1.5 = 50% increase


@dataclass
class Weather:
    """Weather information"""
    temperature_celsius: float
    wind_speed_knots: float
    wind_direction: str
    wave_height_meters: float
    visibility_km: float
    conditions: str
    timestamp: str


@dataclass
class MaintenanceRecord:
    """Maintenance record for berths or marina facilities"""
    maintenance_id: str
    berth_id: Optional[str]
    marina_id: str
    description: str
    scheduled_date: str
    completed_date: Optional[str]
    status: str
    cost: float
    currency: str
    assigned_to: Optional[str]


@dataclass
class Staff:
    """Marina staff member"""
    staff_id: str
    marina_id: str
    name: str
    role: str  # "manager", "dock_master", "maintenance", "security", etc.
    email: str
    phone: str
    shift_start: str
    shift_end: str
    is_active: bool = True


@dataclass
class Berth:
    """Marina berth (rıhtım yeri)"""
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
    daily_rate: float
    currency: str = "EUR"
    status: str = "available"  # "available", "occupied", "maintenance", "reserved"
    current_boat_name: Optional[str] = None
    current_booking_id: Optional[str] = None
    berth_type: str = "standard"  # "standard", "premium", "mega_yacht"
    max_beam_meters: Optional[float] = None
    has_fuel: bool = False
    has_pump_out: bool = False
    has_shore_power_amps: Optional[int] = None
    last_maintenance_date: Optional[str] = None

    def is_suitable_for_boat(self, boat_length: float, boat_beam: Optional[float] = None) -> bool:
        """Check if berth is suitable for boat dimensions"""
        length_ok = self.length_meters >= boat_length + 1.0
        if boat_beam and self.max_beam_meters:
            beam_ok = self.max_beam_meters >= boat_beam + 0.5
            return length_ok and beam_ok
        return length_ok

    def is_available(self) -> bool:
        """Check if berth is available"""
        return self.status == "available"

    @property
    def daily_rate_eur(self) -> float:
        """Backward compatibility: return daily rate as EUR"""
        return self.daily_rate


@dataclass
class Booking:
    """Berth booking"""
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
    total_price: float
    currency: str = "EUR"
    status: str = "pending"  # "pending", "confirmed", "checked_in", "checked_out", "cancelled"
    created_at: str = ""
    services_requested: List[str] = field(default_factory=list)
    boat_registration: Optional[str] = None
    boat_type: Optional[str] = None
    number_of_guests: int = 1
    special_requests: Optional[str] = None
    payment_status: str = "pending"  # "pending", "paid", "refunded"
    payment_method: Optional[str] = None

    @property
    def is_active(self) -> bool:
        """Check if booking is active"""
        return self.status in ["confirmed", "checked_in"]

    @property
    def check_in_date(self) -> datetime:
        """Get check-in as datetime"""
        return datetime.fromisoformat(self.check_in)

    @property
    def check_out_date(self) -> datetime:
        """Get check-out as datetime"""
        return datetime.fromisoformat(self.check_out)

    @property
    def total_price_eur(self) -> float:
        """Backward compatibility: return total price as EUR"""
        return self.total_price


@dataclass
class Marina:
    """Marina facility with comprehensive multi-region support"""
    marina_id: str
    name: str
    location: str
    city: str
    country: str
    country_code: str  # "TR", "GR", "IT", etc.
    total_berths: int
    available_berths: int
    coordinates: Dict[str, float]  # {"lat": 37.0349, "lon": 27.4305}
    amenities: List[str]
    contact_email: str
    contact_phone: str
    currency: str = "EUR"
    timezone: str = "Europe/Athens"
    language: str = "en"
    marina_type: str = "commercial"
    website: Optional[str] = None
    description: Optional[str] = None
    max_boat_length_meters: float = 50.0
    min_depth_meters: float = 2.0
    max_depth_meters: float = 10.0
    fuel_available: bool = True
    diesel_price_per_liter: Optional[float] = None
    gasoline_price_per_liter: Optional[float] = None
    electricity_available: bool = True
    water_available: bool = True
    wifi_available: bool = True
    security_24h: bool = True
    customs_available: bool = False
    repair_services: bool = True
    restaurant: bool = True
    supermarket: bool = False
    laundry: bool = True
    operating_hours: List[OperatingHours] = field(default_factory=list)
    seasonal_pricing: List[SeasonalPricing] = field(default_factory=list)
    tax_rate: float = 0.0  # VAT or local tax rate
    manager_name: Optional[str] = None
    founded_year: Optional[int] = None
    certifications: List[str] = field(default_factory=list)  # Blue Flag, ISO, etc.
    accepts_megayachts: bool = False
    has_travel_lift: bool = False
    travel_lift_capacity_tons: Optional[float] = None

    @property
    def occupancy_rate(self) -> float:
        """Calculate occupancy rate"""
        if self.total_berths == 0:
            return 0.0
        return (self.total_berths - self.available_berths) / self.total_berths * 100

    def has_amenity(self, amenity: str) -> bool:
        """Check if marina has specific amenity"""
        return amenity in self.amenities

    def get_display_name(self) -> str:
        """Get formatted display name with location"""
        return f"{self.name} - {self.city}, {self.country}"

    def is_open_now(self) -> bool:
        """Check if marina is currently open (simplified)"""
        # This would need actual timezone handling in production
        return len(self.operating_hours) > 0
