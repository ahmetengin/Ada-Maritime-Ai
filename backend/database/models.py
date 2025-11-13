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


# ============================================================================
# COMPLIANCE AND SECURITY MODELS (VERIFY Agent)
# ============================================================================

class InsuranceType(Enum):
    """Types of insurance coverage"""
    LIABILITY = "liability"
    HULL = "hull"
    P_AND_I = "p_and_i"  # Protection and Indemnity
    COMPREHENSIVE = "comprehensive"
    THIRD_PARTY = "third_party"


class InsuranceStatus(Enum):
    """Insurance verification status"""
    VALID = "valid"
    EXPIRED = "expired"
    PENDING = "pending"
    REJECTED = "rejected"
    NOT_PROVIDED = "not_provided"


class PermitType(Enum):
    """Types of permits"""
    HOT_WORK = "hot_work"  # Article E.5.5
    COLD_WORK = "cold_work"
    DIVING = "diving"
    CRANE = "crane"
    PAINTING = "painting"
    WASTE_DISPOSAL = "waste_disposal"
    SPECIAL_EVENT = "special_event"


class PermitStatus(Enum):
    """Permit status"""
    REQUESTED = "requested"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ViolationType(Enum):
    """Types of violations"""
    SAFETY = "safety"
    ENVIRONMENTAL = "environmental"
    OPERATIONAL = "operational"
    ADMINISTRATIVE = "administrative"
    SECURITY = "security"
    INSURANCE = "insurance"
    PERMIT = "permit"


class ViolationSeverity(Enum):
    """Violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationStatus(Enum):
    """Violation resolution status"""
    DETECTED = "detected"
    NOTIFIED = "notified"
    IN_RESOLUTION = "in_resolution"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class ComplianceCategory(Enum):
    """Categories for the 176 compliance articles"""
    SAFETY = "safety"
    ENVIRONMENTAL = "environmental"
    OPERATIONAL = "operational"
    ADMINISTRATIVE = "administrative"
    SECURITY = "security"
    INSURANCE_AND_LIABILITY = "insurance_and_liability"
    PERMITS_AND_LICENSES = "permits_and_licenses"


@dataclass
class Insurance:
    """Insurance record for vessels - Article E.2.1 compliance"""
    insurance_id: str
    vessel_name: str
    vessel_registration: str
    booking_id: Optional[str]
    policy_number: str
    insurance_type: str  # InsuranceType
    provider: str
    coverage_amount: float
    currency: str
    issue_date: str  # ISO format
    expiry_date: str  # ISO format
    status: str  # InsuranceStatus
    verified_by: Optional[str] = None
    verified_at: Optional[str] = None
    document_url: Optional[str] = None
    notes: Optional[str] = None
    marina_id: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if insurance is currently valid"""
        if self.status != "valid":
            return False
        try:
            expiry = datetime.fromisoformat(self.expiry_date)
            return expiry > datetime.now()
        except:
            return False

    def days_until_expiry(self) -> int:
        """Calculate days until insurance expires"""
        try:
            expiry = datetime.fromisoformat(self.expiry_date)
            delta = expiry - datetime.now()
            return delta.days
        except:
            return -1

    def requires_renewal_notice(self, days_threshold: int = 30) -> bool:
        """Check if renewal notice should be sent"""
        days_left = self.days_until_expiry()
        return 0 < days_left <= days_threshold


@dataclass
class Permit:
    """Permit record for marina activities - Article E.5.5 (Hot Work) and others"""
    permit_id: str
    permit_type: str  # PermitType
    marina_id: str
    berth_id: Optional[str]
    vessel_name: Optional[str]
    vessel_registration: Optional[str]
    requested_by: str  # Name of requester
    requester_email: str
    requester_phone: str
    work_description: str
    work_location: str  # Specific location in marina
    requested_at: str  # ISO format
    scheduled_start: str  # ISO format
    scheduled_end: str  # ISO format
    status: str  # PermitStatus
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    completed_at: Optional[str] = None
    safety_equipment_required: List[str] = field(default_factory=list)
    fire_watch_required: bool = False
    fire_watch_personnel: Optional[str] = None
    safety_zone_meters: Optional[float] = None
    conditions: List[str] = field(default_factory=list)
    violation_logged: bool = False
    notes: Optional[str] = None

    def is_active(self) -> bool:
        """Check if permit is currently active"""
        if self.status != "active":
            return False
        try:
            start = datetime.fromisoformat(self.scheduled_start)
            end = datetime.fromisoformat(self.scheduled_end)
            now = datetime.now()
            return start <= now <= end
        except:
            return False

    def is_expired(self) -> bool:
        """Check if permit has expired"""
        try:
            end = datetime.fromisoformat(self.scheduled_end)
            return datetime.now() > end
        except:
            return True

    def requires_fire_watch(self) -> bool:
        """Check if fire watch is required (hot work permits)"""
        return self.permit_type == "hot_work" or self.fire_watch_required


@dataclass
class ComplianceRule:
    """Compliance rule definition - Part of 176-article system"""
    rule_id: str
    article_number: str  # e.g., "E.2.1", "E.5.5"
    title: str
    description: str
    category: str  # ComplianceCategory
    severity: str  # ViolationSeverity if violated
    conditions: Dict[str, any] = field(default_factory=dict)  # Rule evaluation conditions
    auto_check: bool = True  # Can be automatically checked
    check_frequency_hours: int = 24  # How often to check
    notification_emails: List[str] = field(default_factory=list)
    escalation_threshold_hours: int = 24  # Hours before escalation
    is_active: bool = True
    applies_to: List[str] = field(default_factory=list)  # ["all", "vessels", "marina", "staff"]

    def should_check_now(self, last_check: Optional[datetime] = None) -> bool:
        """Determine if rule should be checked now"""
        if not self.auto_check or not self.is_active:
            return False
        if last_check is None:
            return True
        hours_since_check = (datetime.now() - last_check).total_seconds() / 3600
        return hours_since_check >= self.check_frequency_hours


@dataclass
class Violation:
    """Compliance violation record"""
    violation_id: str
    rule_id: str
    article_number: str
    marina_id: str
    violation_type: str  # ViolationType
    severity: str  # ViolationSeverity
    detected_at: str  # ISO format
    description: str
    status: str  # ViolationStatus
    entity_type: str  # "vessel", "berth", "marina", "staff"
    entity_id: str  # ID of the violating entity
    vessel_name: Optional[str] = None
    berth_id: Optional[str] = None
    booking_id: Optional[str] = None
    permit_id: Optional[str] = None
    insurance_id: Optional[str] = None
    notified_parties: List[str] = field(default_factory=list)
    notified_at: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    escalated_at: Optional[str] = None
    escalated_to: Optional[str] = None
    evidence: Dict[str, any] = field(default_factory=dict)

    def is_resolved(self) -> bool:
        """Check if violation has been resolved"""
        return self.status == "resolved"

    def hours_since_detection(self) -> float:
        """Calculate hours since violation was detected"""
        try:
            detected = datetime.fromisoformat(self.detected_at)
            return (datetime.now() - detected).total_seconds() / 3600
        except:
            return 0.0

    def should_escalate(self, threshold_hours: int = 24) -> bool:
        """Check if violation should be escalated"""
        if self.is_resolved() or self.status == "escalated":
            return False
        return self.hours_since_detection() >= threshold_hours


@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: str
    marina_id: str
    incident_type: str  # "unauthorized_access", "theft", "vandalism", "fire", "medical", "other"
    severity: str  # ViolationSeverity
    occurred_at: str  # ISO format
    reported_at: str  # ISO format
    reported_by: str
    location: str
    description: str
    berth_id: Optional[str] = None
    vessel_name: Optional[str] = None
    witnesses: List[str] = field(default_factory=list)
    authorities_notified: bool = False
    authority_reference: Optional[str] = None
    response_actions: List[str] = field(default_factory=list)
    status: str = "open"  # "open", "investigating", "resolved", "closed"
    resolved_at: Optional[str] = None
    resolution_notes: Optional[str] = None
    evidence_urls: List[str] = field(default_factory=list)

    def is_critical(self) -> bool:
        """Check if incident is critical"""
        return self.severity == "critical" or self.incident_type in ["fire", "medical"]


@dataclass
class Document:
    """Document record for compliance verification"""
    document_id: str
    document_type: str  # "insurance", "certificate", "permit", "license", "inspection"
    entity_type: str  # "vessel", "marina", "staff"
    entity_id: str
    title: str
    issuing_authority: str
    issue_date: str  # ISO format
    expiry_date: Optional[str] = None
    verification_status: str = "pending"  # "pending", "verified", "rejected", "expired"
    verified_by: Optional[str] = None
    verified_at: Optional[str] = None
    file_url: Optional[str] = None
    file_hash: Optional[str] = None
    notes: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if document has expired"""
        if not self.expiry_date:
            return False
        try:
            expiry = datetime.fromisoformat(self.expiry_date)
            return datetime.now() > expiry
        except:
            return False

    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until document expires"""
        if not self.expiry_date:
            return None
        try:
            expiry = datetime.fromisoformat(self.expiry_date)
            delta = expiry - datetime.now()
            return delta.days
        except:
            return None


# ============================================================================
# VHF COMMUNICATION MODELS
# ============================================================================

class VHFChannelType(Enum):
    """VHF channel types"""
    DISTRESS = "distress"  # Channel 16 - emergency
    INTERSHIP = "intership"  # Ship-to-ship / gemiden gemiye
    MARINA = "marina"  # Marina operations
    PORT_OPS = "port_ops"  # Port operations
    BRIDGE_TO_BRIDGE = "bridge_to_bridge"  # Köprü-köprü
    WORKING = "working"  # General working channels
    PUBLIC_CORRESPONDENCE = "public_correspondence"  # Telefon
    WEATHER = "weather"  # Meteoroloji
    NAVIGATION = "navigation"  # Navigasyon güvenliği


class VHFMode(Enum):
    """VHF operating modes"""
    SIMPLEX = "simplex"  # Single frequency
    DUPLEX = "duplex"  # Two frequencies


class VHFRegion(Enum):
    """VHF regulatory regions"""
    INTERNATIONAL = "international"
    TURKEY = "turkey"
    MEDITERRANEAN = "mediterranean"
    EU = "eu"
    USA = "usa"


@dataclass
class VHFChannel:
    """VHF Radio Channel Definition"""
    channel_number: int  # e.g., 16, 72, 73
    frequency_mhz: float  # e.g., 156.800
    channel_type: str  # VHFChannelType
    usage_description: str
    mode: str = "simplex"  # VHFMode
    power_restriction: Optional[str] = None  # "1W", "25W", etc.
    region: str = "international"  # VHFRegion
    is_priority: bool = False  # Priority monitoring
    notes: Optional[str] = None

    def get_display_name(self) -> str:
        """Get formatted channel display"""
        return f"CH {self.channel_number:02d} ({self.frequency_mhz} MHz)"

    def is_intership_channel(self) -> bool:
        """Check if this is an intership communication channel"""
        return self.channel_type == "intership"

    def is_emergency_channel(self) -> bool:
        """Check if this is an emergency/distress channel"""
        return self.channel_type == "distress" or self.channel_number == 16


@dataclass
class MarinaVHFConfig:
    """VHF Channel Configuration for a Marina"""
    marina_id: str
    marina_name: str
    primary_channel: int  # Main marina calling channel
    primary_frequency: float
    working_channels: List[int] = field(default_factory=list)  # Additional working channels
    intership_channels: List[int] = field(default_factory=list)  # Recommended intership
    monitoring_channels: List[int] = field(default_factory=list)  # Channels to monitor
    call_sign: Optional[str] = None  # Marina radio call sign
    operating_hours: Optional[str] = None  # When VHF is manned
    languages: List[str] = field(default_factory=lambda: ["Turkish", "English"])
    notes: Optional[str] = None

    def get_all_channels(self) -> List[int]:
        """Get all channels used by this marina"""
        channels = [self.primary_channel]
        channels.extend(self.working_channels)
        channels.extend(self.monitoring_channels)
        return sorted(list(set(channels)))


@dataclass
class IntershipCommunication:
    """Intership communication record"""
    comm_id: str
    timestamp: str  # ISO format
    channel_number: int
    frequency_mhz: float
    vessel1_name: Optional[str] = None
    vessel2_name: Optional[str] = None
    duration_seconds: Optional[float] = None
    content_summary: Optional[str] = None  # From STT/AI
    communication_type: str = "operational"  # operational, safety, social, race
    location: Optional[Dict[str, float]] = None  # {"lat": 41.0, "lon": 29.0}
    detected_by: str = "sdr"  # sdr, manual, radio_log
    signal_strength: Optional[float] = None  # RSSI
    audio_file_url: Optional[str] = None
    transcription: Optional[str] = None


@dataclass
class VHFMonitoringSession:
    """VHF Monitoring Session (for Ada Observer)"""
    session_id: str
    start_time: str  # ISO format
    end_time: Optional[str] = None
    channels_monitored: List[int] = field(default_factory=list)
    location: Optional[Dict[str, float]] = None
    vessel_name: Optional[str] = None
    mode: str = "passive"  # passive, active, race_net
    detected_communications: List[str] = field(default_factory=list)  # comm_ids
    priority_channels: List[int] = field(default_factory=lambda: [16, 72, 73])
    scan_interval_seconds: float = 1.0
    is_active: bool = True

    def add_communication(self, comm_id: str) -> None:
        """Add detected communication to session"""
        self.detected_communications.append(comm_id)

    def get_duration_minutes(self) -> Optional[float]:
        """Calculate session duration in minutes"""
        if not self.end_time:
            return None
        try:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            return (end - start).total_seconds() / 60
        except:
            return None
