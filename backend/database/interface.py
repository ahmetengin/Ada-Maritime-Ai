"""Database interface for Ada Maritime AI - Airport-Style Parallel Operations"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from .models import Berth, Booking, Marina, Vessel, Gate, Terminal, ServiceQueue, TrafficData, GateAssignment


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

    # ============================================================================
    # AIRPORT-STYLE PARALLEL OPERATIONS METHODS
    # ============================================================================

    # Vessel operations (parallel-ready)
    @abstractmethod
    async def get_vessel(self, vessel_id: str) -> Optional[Vessel]:
        """Get vessel by ID (async)"""
        pass

    @abstractmethod
    async def get_vessels_batch(self, vessel_ids: List[str]) -> List[Vessel]:
        """Get multiple vessels in batch (async)"""
        pass

    @abstractmethod
    async def update_vessel_status(self, vessel_id: str, status: str) -> bool:
        """Update vessel status (async)"""
        pass

    @abstractmethod
    async def update_vessel_status_batch(
        self,
        updates: List[Tuple[str, str]]
    ) -> List[bool]:
        """Update multiple vessel statuses in batch (async)"""
        pass

    # Gate operations (parallel-ready)
    @abstractmethod
    async def get_gate(self, gate_id: str) -> Optional[Gate]:
        """Get gate by ID (async)"""
        pass

    @abstractmethod
    async def search_suitable_gates(
        self,
        vessel: Vessel,
        terminal_id: Optional[str] = None,
        time_window: Optional[Dict] = None
    ) -> List[Gate]:
        """Search for suitable gates for a vessel (async)"""
        pass

    @abstractmethod
    async def search_available_gates_batch(
        self,
        vessels: List[Vessel],
        time_window: Optional[Tuple[datetime, datetime]] = None
    ) -> List[List[Gate]]:
        """
        Search available gates for multiple vessels (async)
        Returns list of candidate gates for each vessel
        """
        pass

    @abstractmethod
    async def allocate_gate(
        self,
        vessel_id: str,
        gate_id: str,
        duration_hours: int = 24
    ) -> bool:
        """Allocate gate to vessel atomically (async)"""
        pass

    @abstractmethod
    async def allocate_gates_batch(
        self,
        allocations: List[Tuple[str, str, int]]
    ) -> List[bool]:
        """
        Allocate multiple gates in batch (async)
        Args: [(vessel_id, gate_id, duration_hours), ...]
        """
        pass

    @abstractmethod
    async def release_gate(self, gate_id: str) -> bool:
        """Release gate from current assignment (async)"""
        pass

    # Terminal operations
    @abstractmethod
    async def get_terminal(self, terminal_id: str) -> Optional[Terminal]:
        """Get terminal by ID (async)"""
        pass

    @abstractmethod
    async def get_all_terminals(self, port_id: Optional[str] = None) -> List[Terminal]:
        """Get all terminals, optionally filtered by port (async)"""
        pass

    # Traffic and congestion monitoring
    @abstractmethod
    async def get_current_traffic_data(self, port_id: str) -> Optional[TrafficData]:
        """Get current traffic data for a port (async)"""
        pass

    @abstractmethod
    async def get_traffic_forecast(
        self,
        port_id: str,
        hours_ahead: int
    ) -> List[TrafficData]:
        """Get traffic forecast for next N hours (async)"""
        pass

    # Service queue management
    @abstractmethod
    async def add_to_service_queue(
        self,
        service_type: str,
        vessel_id: str,
        terminal_id: str,
        priority: int = 5
    ) -> bool:
        """Add vessel to service queue (async)"""
        pass

    @abstractmethod
    async def get_service_queue_status(
        self,
        service_type: str,
        terminal_id: str
    ) -> Optional[ServiceQueue]:
        """Get service queue status (async)"""
        pass

    @abstractmethod
    async def get_next_from_queue(
        self,
        service_type: str,
        terminal_id: str
    ) -> Optional[str]:
        """Get next vessel from service queue (async)"""
        pass

    # Resource allocation
    @abstractmethod
    async def get_resource_availability(
        self,
        resource_type: str,
        vessel_id: str
    ) -> Dict[str, Any]:
        """Check resource availability for vessel (async)"""
        pass

    @abstractmethod
    async def allocate_resource(
        self,
        vessel_id: str,
        resource_type: str,
        quantity: int
    ) -> bool:
        """Allocate resource to vessel (async)"""
        pass

    # Transaction support for atomic operations
    @abstractmethod
    async def begin_transaction(self) -> str:
        """Begin database transaction, returns transaction_id (async)"""
        pass

    @abstractmethod
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit transaction (async)"""
        pass

    @abstractmethod
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback transaction (async)"""
        pass

    # Gate assignment records
    @abstractmethod
    async def create_gate_assignment(
        self,
        vessel_id: str,
        gate_id: str,
        terminal_id: str,
        scheduled_arrival: datetime,
        scheduled_departure: datetime,
        services_required: List[str]
    ) -> Optional[GateAssignment]:
        """Create gate assignment record (async)"""
        pass

    @abstractmethod
    async def get_gate_assignments(
        self,
        terminal_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[GateAssignment]:
        """Get gate assignments, optionally filtered (async)"""
        pass

    @abstractmethod
    async def update_gate_assignment_status(
        self,
        assignment_id: str,
        status: str,
        actual_time: Optional[datetime] = None
    ) -> bool:
        """Update gate assignment status (async)"""
        pass
