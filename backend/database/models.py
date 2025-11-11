"""Data models for Ada Maritime AI - Airport-Style Parallel Management"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


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


# ============================================================================
# AIRPORT-STYLE PARALLEL MANAGEMENT MODELS
# ============================================================================

class VesselType(Enum):
    """Vessel types for classification"""
    COMMERCIAL = "commercial"
    PASSENGER = "passenger"
    CARGO = "cargo"
    YACHT = "yacht"
    FERRY = "ferry"
    FISHING = "fishing"


class VesselStatus(Enum):
    """Current vessel operational status"""
    IN_TRANSIT = "in_transit"
    APPROACHING = "approaching"
    DOCKED = "docked"
    BOARDING = "boarding"
    REFUELING = "refueling"
    MAINTENANCE = "maintenance"
    DEPARTING = "departing"


class GateStatus(Enum):
    """Gate/Berth operational status"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"


@dataclass
class Vessel:
    """Enhanced vessel model for airport-style operations"""
    vessel_id: str
    vessel_name: str
    vessel_type: VesselType
    length_meters: float
    width_meters: float
    draft_meters: float  # Water depth requirement
    passenger_capacity: int
    cargo_capacity_tons: float
    current_location: str
    current_status: VesselStatus
    owner_id: str
    captain_id: str
    captain_name: str
    last_maintenance: datetime
    next_maintenance: datetime
    required_services: List[str] = field(default_factory=list)
    special_requirements: List[str] = field(default_factory=list)
    estimated_arrival: Optional[datetime] = None
    estimated_departure: Optional[datetime] = None
    current_gate_id: Optional[str] = None
    priority_level: int = 5  # 1-10, higher = more priority

    @property
    def is_due_for_maintenance(self) -> bool:
        """Check if vessel is due for maintenance"""
        return datetime.now() >= self.next_maintenance

    @property
    def requires_deep_berth(self) -> bool:
        """Check if vessel requires deep water berth"""
        return self.draft_meters > 3.0

    def can_dock_at_gate(self, gate: 'Gate') -> bool:
        """Check if vessel can physically dock at gate"""
        return (gate.length_meters >= self.length_meters and
                gate.width_meters >= self.width_meters and
                gate.depth_meters >= self.draft_meters and
                gate.max_passenger_capacity >= self.passenger_capacity)


@dataclass
class Gate:
    """Terminal gate/berth infrastructure (Airport-style)"""
    gate_id: str
    terminal_id: str
    gate_number: str
    location: str  # GPS coordinates or section identifier
    length_meters: float
    width_meters: float
    depth_meters: float
    max_passenger_capacity: int
    max_cargo_capacity_tons: float
    gate_type: str  # "boarding", "cargo", "fuel", "maintenance", "vip"
    equipment: List[str] = field(default_factory=list)
    status: GateStatus = GateStatus.AVAILABLE
    current_vessel_id: Optional[str] = None
    allocated_until: Optional[datetime] = None
    daily_rate_eur: float = 0.0
    hourly_rate_eur: float = 0.0

    def is_available(self) -> bool:
        """Check if gate is available for assignment"""
        if self.status != GateStatus.AVAILABLE:
            return False
        if self.allocated_until and datetime.now() < self.allocated_until:
            return False
        return True

    def is_suitable_for_vessel(self, vessel: Vessel) -> bool:
        """Check if gate is suitable for vessel"""
        return vessel.can_dock_at_gate(self)

    def calculate_cost(self, duration_hours: int) -> float:
        """Calculate docking cost for given duration"""
        if duration_hours < 24:
            return self.hourly_rate_eur * duration_hours
        else:
            days = duration_hours / 24
            return self.daily_rate_eur * days


@dataclass
class Terminal:
    """Terminal facility (like airport terminal)"""
    terminal_id: str
    port_id: str
    name: str
    gates: List[Gate] = field(default_factory=list)
    total_gates: int = 0
    amenities: List[str] = field(default_factory=list)
    current_congestion: float = 0.0  # 0-100%
    max_simultaneous_operations: int = 10

    @property
    def available_gates(self) -> int:
        """Count available gates"""
        return sum(1 for gate in self.gates if gate.is_available())

    @property
    def occupancy_rate(self) -> float:
        """Calculate terminal occupancy rate"""
        if self.total_gates == 0:
            return 0.0
        return (self.total_gates - self.available_gates) / self.total_gates * 100

    def get_available_gates_for_vessel(self, vessel: Vessel) -> List[Gate]:
        """Get all available gates suitable for vessel"""
        return [gate for gate in self.gates
                if gate.is_available() and gate.is_suitable_for_vessel(vessel)]


@dataclass
class ServiceQueue:
    """Service queue for parallel resource management"""
    queue_id: str
    service_type: str  # "refueling", "catering", "maintenance", "customs", "cleaning"
    terminal_id: str
    avg_duration_minutes: int
    max_concurrent_services: int = 3
    vessels_waiting: List[str] = field(default_factory=list)
    vessels_in_service: List[str] = field(default_factory=list)
    priority_levels: Dict[str, int] = field(default_factory=dict)

    @property
    def queue_length(self) -> int:
        """Get current queue length"""
        return len(self.vessels_waiting)

    @property
    def is_at_capacity(self) -> bool:
        """Check if service is at maximum capacity"""
        return len(self.vessels_in_service) >= self.max_concurrent_services

    @property
    def estimated_wait_time(self) -> int:
        """Estimate wait time for new vessel (minutes)"""
        if not self.is_at_capacity:
            return 0
        queue_position = self.queue_length + 1
        services_ahead = queue_position + len(self.vessels_in_service)
        return (services_ahead * self.avg_duration_minutes) // self.max_concurrent_services

    def add_vessel(self, vessel_id: str, priority: int = 5) -> int:
        """Add vessel to queue, return estimated wait time"""
        self.vessels_waiting.append(vessel_id)
        self.priority_levels[vessel_id] = priority
        return self.estimated_wait_time

    def get_next_vessel(self) -> Optional[str]:
        """Get next vessel to service (based on priority)"""
        if not self.vessels_waiting:
            return None
        # Sort by priority (higher first)
        sorted_vessels = sorted(
            self.vessels_waiting,
            key=lambda v: self.priority_levels.get(v, 5),
            reverse=True
        )
        next_vessel = sorted_vessels[0]
        self.vessels_waiting.remove(next_vessel)
        self.vessels_in_service.append(next_vessel)
        return next_vessel


@dataclass
class TrafficData:
    """Real-time traffic and congestion data"""
    timestamp: datetime
    port_id: str
    vessels_in_port: int
    vessels_approaching: int
    vessels_departing: int
    arrival_queue_length: int
    departure_queue_length: int
    avg_docking_time_minutes: int
    avg_departure_time_minutes: int
    weather_condition: str  # "clear", "foggy", "rainy", "storm", "severe"
    wind_speed_knots: float
    wave_height_meters: float
    visibility_meters: float
    congestion_level: str  # "low", "medium", "high", "critical"
    estimated_wait_time_minutes: int
    available_berths: int
    channel_availability: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)

    @property
    def is_safe_for_operations(self) -> bool:
        """Check if weather conditions are safe for operations"""
        return (self.weather_condition not in ["storm", "severe"] and
                self.wind_speed_knots < 35 and
                self.wave_height_meters < 2.5 and
                self.visibility_meters > 500)

    @property
    def congestion_score(self) -> float:
        """Calculate congestion score (0-100)"""
        factors = {
            "queue": min(self.arrival_queue_length * 10, 40),
            "occupancy": min((self.vessels_in_port / max(self.available_berths, 1)) * 30, 30),
            "weather": 30 if not self.is_safe_for_operations else 0
        }
        return sum(factors.values())


@dataclass
class GateAssignment:
    """Gate assignment record for tracking"""
    assignment_id: str
    vessel_id: str
    gate_id: str
    terminal_id: str
    scheduled_arrival: datetime
    scheduled_departure: datetime
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    status: str = "scheduled"  # "scheduled", "arrived", "departed", "cancelled"
    services_required: List[str] = field(default_factory=list)
    services_completed: List[str] = field(default_factory=list)
    total_cost_eur: float = 0.0

    @property
    def duration_hours(self) -> float:
        """Calculate scheduled duration in hours"""
        delta = self.scheduled_departure - self.scheduled_arrival
        return delta.total_seconds() / 3600

    @property
    def actual_duration_hours(self) -> Optional[float]:
        """Calculate actual duration if completed"""
        if self.actual_arrival and self.actual_departure:
            delta = self.actual_departure - self.actual_arrival
            return delta.total_seconds() / 3600
        return None

    @property
    def is_delayed(self) -> bool:
        """Check if arrival is delayed"""
        if self.actual_arrival:
            return self.actual_arrival > self.scheduled_arrival
        return False


@dataclass
class Conflict:
    """Conflict detection for parallel operations"""
    conflict_id: str
    conflict_type: str  # "gate_overlap", "resource_shortage", "time_conflict"
    severity: str  # "low", "medium", "high", "critical"
    vessel_ids: List[str]
    gate_id: Optional[str] = None
    resource_type: Optional[str] = None
    description: str = ""
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_strategy: Optional[str] = None

    def __str__(self) -> str:
        """String representation of conflict"""
        return f"Conflict({self.conflict_type}, severity={self.severity}, vessels={len(self.vessel_ids)})"


# ============================================================================
# AIRPORT-STYLE DEPARTURE/ARRIVAL OPERATIONS (Pushback, Taxi, Follow-Me)
# ============================================================================

class DeparturePhase(Enum):
    """Departure phases like airport operations"""
    AT_BERTH = "at_berth"                      # Henüz berth'te
    PUSHBACK_REQUESTED = "pushback_requested"  # Pushback (palamar botu) talep edildi
    PUSHBACK_IN_PROGRESS = "pushback_in_progress"  # Palamarlar çözülüyor
    TAXI_CLEARANCE = "taxi_clearance"          # Marina içi hareket izni
    TAXIING = "taxiing"                        # Marina içinde hareket ediyor
    FOLLOW_ME_ACTIVE = "follow_me_active"      # Rehber bot eşlik ediyor
    HOLDING_POINT = "holding_point"            # Çıkış kanalı girişinde bekliyor
    DEPARTURE_CLEARANCE = "departure_clearance"  # Çıkış izni alındı
    DEPARTING = "departing"                    # Çıkış kanalında
    CLEAR_OF_MARINA = "clear_of_marina"        # Marina sınırından çıktı


class ArrivalPhase(Enum):
    """Arrival phases like airport operations"""
    APPROACHING = "approaching"                # Marina'ya yaklaşıyor
    ENTRY_CLEARANCE = "entry_clearance"        # Giriş izni alındı
    IN_CHANNEL = "in_channel"                  # Giriş kanalında
    FOLLOW_ME_ASSIGNED = "follow_me_assigned"  # Rehber bot atandı
    TAXIING_TO_BERTH = "taxiing_to_berth"     # Berth'e doğru hareket
    MOORING_REQUESTED = "mooring_requested"    # Palamar botu talep edildi
    MOORING_IN_PROGRESS = "mooring_in_progress"  # Palamar atılıyor
    DOCKED = "docked"                          # Yanaştı, palamarlar bağlandı


@dataclass
class MooringBoat:
    """Palamar botu (Pushback truck gibi)"""
    boat_id: str
    boat_name: str
    capacity: int  # Aynı anda kaç tekneye hizmet verebilir
    current_status: str  # "available", "busy", "maintenance"
    current_assignment: Optional[str] = None  # Şu anda hangi vessel'a hizmet veriyor
    location: str = ""
    equipment: List[str] = field(default_factory=list)  # ["fenders", "lines", "radio"]
    crew_size: int = 2
    response_time_minutes: int = 5  # Ortalama ulaşma süresi

    def is_available(self) -> bool:
        """Check if mooring boat is available"""
        return self.current_status == "available" and self.current_assignment is None


@dataclass
class PilotBoat:
    """Rehber bot (Follow-me car gibi)"""
    boat_id: str
    boat_name: str
    current_status: str  # "available", "escorting", "returning", "maintenance"
    current_vessel_id: Optional[str] = None
    location: str = ""
    pilot_name: str = ""
    vhf_channel: int = 16  # VHF iletişim kanalı
    max_escort_speed_knots: float = 5.0

    def is_available(self) -> bool:
        """Check if pilot boat is available"""
        return self.current_status == "available" and self.current_vessel_id is None


@dataclass
class DepartureChannel:
    """Çıkış kanalı (Runway gibi)"""
    channel_id: str
    channel_name: str
    width_meters: float
    depth_meters: float
    length_meters: float
    max_vessel_length: float
    status: str  # "open", "closed", "restricted", "one_way_inbound", "one_way_outbound"
    current_traffic: List[str] = field(default_factory=list)  # vessel_id'ler
    max_simultaneous_vessels: int = 1  # Genelde 1, tek yönlü
    weather_restrictions: List[str] = field(default_factory=list)
    tide_restrictions: bool = False

    def is_available_for_departure(self) -> bool:
        """Check if channel is available for departure"""
        return (self.status in ["open", "one_way_outbound"] and
                len(self.current_traffic) < self.max_simultaneous_vessels)

    def is_available_for_arrival(self) -> bool:
        """Check if channel is available for arrival"""
        return (self.status in ["open", "one_way_inbound"] and
                len(self.current_traffic) < self.max_simultaneous_vessels)


@dataclass
class DepartureSequence:
    """
    Departure operation sequence (Airport-style)
    Tüm ayrılış sürecini takip eder
    """
    sequence_id: str
    vessel_id: str
    berth_id: str
    terminal_id: str

    # Timing
    requested_departure_time: datetime
    actual_departure_time: Optional[datetime] = None

    # Phase tracking
    current_phase: DeparturePhase = DeparturePhase.AT_BERTH
    phase_history: List[Dict[str, Any]] = field(default_factory=list)

    # Resources
    mooring_boat_id: Optional[str] = None
    pilot_boat_id: Optional[str] = None
    departure_channel_id: Optional[str] = None

    # Communication
    vhf_channel: int = 16
    clearances: List[str] = field(default_factory=list)  # İzinler

    # Status
    status: str = "scheduled"  # "scheduled", "in_progress", "completed", "cancelled"
    delays: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def update_phase(self, new_phase: DeparturePhase, timestamp: Optional[datetime] = None):
        """Update departure phase and record history"""
        if timestamp is None:
            timestamp = datetime.now()

        old_phase_time = self._get_last_phase_time()

        self.phase_history.append({
            "phase": self.current_phase.value,
            "timestamp": timestamp.isoformat(),
            "duration_seconds": (timestamp - old_phase_time).total_seconds()
        })

        self.current_phase = new_phase

    def _get_last_phase_time(self) -> datetime:
        """Get timestamp of last phase change"""
        if self.phase_history:
            return datetime.fromisoformat(self.phase_history[-1]["timestamp"])
        return datetime.now()

    def add_clearance(self, clearance: str):
        """Add clearance to list"""
        self.clearances.append(f"{datetime.now().isoformat()}: {clearance}")

    def add_delay(self, reason: str, duration_minutes: int):
        """Record a delay"""
        self.delays.append({
            "reason": reason,
            "duration_minutes": duration_minutes,
            "timestamp": datetime.now().isoformat()
        })

    @property
    def total_delay_minutes(self) -> int:
        """Calculate total delay"""
        return sum(d["duration_minutes"] for d in self.delays)

    @property
    def estimated_completion_time(self) -> datetime:
        """Estimate when departure will be complete"""
        # Ortalama süre: Pushback (5min) + Taxi (10min) + Departure (5min) = 20min
        base_duration = timedelta(minutes=20)
        delay_duration = timedelta(minutes=self.total_delay_minutes)

        return self.requested_departure_time + base_duration + delay_duration


@dataclass
class ArrivalSequence:
    """
    Arrival operation sequence (Airport-style)
    Tüm varış sürecini takip eder
    """
    sequence_id: str
    vessel_id: str
    destination_berth_id: str
    terminal_id: str

    # Timing
    estimated_arrival_time: datetime
    actual_arrival_time: Optional[datetime] = None

    # Phase tracking
    current_phase: ArrivalPhase = ArrivalPhase.APPROACHING
    phase_history: List[Dict[str, Any]] = field(default_factory=list)

    # Resources
    pilot_boat_id: Optional[str] = None
    mooring_boat_id: Optional[str] = None
    arrival_channel_id: Optional[str] = None

    # Communication
    vhf_channel: int = 16
    clearances: List[str] = field(default_factory=list)

    # Status
    status: str = "scheduled"  # "scheduled", "in_progress", "completed", "cancelled"
    delays: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def update_phase(self, new_phase: ArrivalPhase):
        """Update arrival phase"""
        self.phase_history.append({
            "phase": self.current_phase.value,
            "timestamp": datetime.now().isoformat()
        })
        self.current_phase = new_phase

    def add_clearance(self, clearance: str):
        """Add clearance"""
        self.clearances.append(f"{datetime.now().isoformat()}: {clearance}")


@dataclass
class MarinaControl:
    """
    Marina kontrol kulesi (Airport control tower gibi)
    Tüm giriş-çıkış trafiğini yönetir
    """
    control_id: str
    marina_id: str
    primary_vhf_channel: int = 16
    secondary_vhf_channel: int = 71

    # Active operations
    active_departures: List[str] = field(default_factory=list)  # DepartureSequence IDs
    active_arrivals: List[str] = field(default_factory=list)    # ArrivalSequence IDs

    # Resources
    available_mooring_boats: List[str] = field(default_factory=list)
    available_pilot_boats: List[str] = field(default_factory=list)

    # Channel status
    departure_channels: List[str] = field(default_factory=list)
    arrival_channels: List[str] = field(default_factory=list)

    # Traffic management
    departure_queue: List[str] = field(default_factory=list)  # Vessel IDs waiting to depart
    arrival_queue: List[str] = field(default_factory=list)    # Vessel IDs waiting to arrive

    # Weather and conditions
    current_weather: Optional[str] = None
    wind_speed_knots: float = 0.0
    visibility_meters: float = 10000.0
    operations_status: str = "normal"  # "normal", "restricted", "closed"

    def can_clear_departure(self, vessel_id: str) -> Tuple[bool, str]:
        """Check if vessel can be cleared for departure"""
        if self.operations_status == "closed":
            return False, "Marina operations closed due to weather"

        if not self.available_mooring_boats:
            return False, "No mooring boats available"

        if not self.departure_channels:
            return False, "No departure channels available"

        return True, "Cleared for departure"

    def can_clear_arrival(self, vessel_id: str) -> Tuple[bool, str]:
        """Check if vessel can be cleared for arrival"""
        if self.operations_status == "closed":
            return False, "Marina operations closed due to weather"

        if not self.available_pilot_boats:
            return False, "No pilot boats available - hold position"

        if not self.arrival_channels:
            return False, "No arrival channels available - hold outside marina"

        return True, "Cleared for arrival"
