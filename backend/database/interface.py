"""Database interface for Ada Maritime AI"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .models import Berth, Booking, Marina


class DatabaseInterface(ABC):
    """Abstract database interface"""
    
    @abstractmethod
    def get_marina_by_id(self, marina_id: str) -> Optional[Marina]:
        """Get marina by ID"""
        pass
    
    @abstractmethod
    def get_all_marinas(self) -> List[Marina]:
        """Get all marinas"""
        pass
    
    @abstractmethod
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
        """Search for available berths"""
        pass
    
    @abstractmethod
    def get_berth_by_id(self, berth_id: str) -> Optional[Berth]:
        """Get berth by ID"""
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        pass
    
    @abstractmethod
    def get_bookings_by_marina(self, marina_id: str) -> List[Booking]:
        """Get all bookings for a marina"""
        pass

    @abstractmethod
    def get_all_berths(self) -> List[Berth]:
        """Get all berths"""
        pass
