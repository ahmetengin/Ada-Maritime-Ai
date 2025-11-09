"""Data models for Ada Maritime AI"""

from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


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
    daily_rate_eur: float
    status: str  # "available", "occupied", "maintenance", "reserved"
    current_boat_name: Optional[str] = None
    current_booking_id: Optional[str] = None
    
    def is_suitable_for_boat(self, boat_length: float) -> bool:
        """Check if berth is suitable for boat length"""
        return self.length_meters >= boat_length + 1.0
    
    def is_available(self) -> bool:
        """Check if berth is available"""
        return self.status == "available"


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
    total_price_eur: float
    status: str  # "pending", "confirmed", "checked_in", "checked_out", "cancelled"
    created_at: str
    services_requested: List[str]
    
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


@dataclass
class Marina:
    """Marina facility"""
    marina_id: str
    name: str
    location: str
    country: str
    total_berths: int
    available_berths: int
    coordinates: dict
    amenities: List[str]
    contact_email: str
    contact_phone: str
    
    @property
    def occupancy_rate(self) -> float:
        """Calculate occupancy rate"""
        if self.total_berths == 0:
            return 0.0
        return (self.total_berths - self.available_berths) / self.total_berths * 100
    
    def has_amenity(self, amenity: str) -> bool:
        """Check if marina has specific amenity"""
        return amenity in self.amenities
