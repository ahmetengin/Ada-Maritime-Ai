"""
Data Classification and Permission System
Granular control over data sharing based on sensitivity levels
"""

from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass, field


class PermissionLevel(Enum):
    """Data permission levels - from most restrictive to least"""

    # LEVEL 0: Never share without explicit command
    PRIVATE = "private"

    # LEVEL 1: Share only essential data with captain approval
    RESTRICTED = "restricted"

    # LEVEL 2: Can share with captain consent (one-time or standing)
    CONDITIONAL = "conditional"

    # LEVEL 3: Anonymous/aggregated only
    ANONYMOUS = "anonymous"


class DataClassification(Enum):
    """Categories of data by sensitivity"""

    # Never share automatically
    GPS_HISTORY = "gps_history"
    COMMUNICATION_LOGS = "communication_logs"
    FINANCIAL_DATA = "financial_data"
    CREW_PERSONAL_INFO = "crew_personal_info"
    SENSOR_RAW_DATA = "sensor_raw_data"
    SECURITY_CAMERAS = "security_cameras"
    PASSWORDS = "passwords"
    API_KEYS = "api_keys"

    # Share only when needed with approval
    CURRENT_POSITION = "current_position"
    VESSEL_SPECIFICATIONS = "vessel_specifications"
    ARRIVAL_TIME = "arrival_time"
    CONTACT_INFO = "contact_info"

    # Conditional sharing
    WEATHER_PREFERENCES = "weather_preferences"
    ROUTE_PLANNING_STYLE = "route_planning_style"
    FUEL_CONSUMPTION_STATS = "fuel_consumption_stats"
    MAINTENANCE_SCHEDULE = "maintenance_schedule"

    # Anonymous only
    POPULAR_ROUTES = "popular_routes"
    ANCHORAGE_RATINGS = "anchorage_ratings"
    WEATHER_REPORTS = "weather_reports"


@dataclass
class DataPolicy:
    """
    Data sharing policy configuration
    Maps data types to permission levels
    """

    # Data classification mapping
    classification_map: Dict[DataClassification, PermissionLevel] = field(
        default_factory=lambda: {
            # LEVEL 0: PRIVATE - Never share without explicit command
            DataClassification.GPS_HISTORY: PermissionLevel.PRIVATE,
            DataClassification.COMMUNICATION_LOGS: PermissionLevel.PRIVATE,
            DataClassification.FINANCIAL_DATA: PermissionLevel.PRIVATE,
            DataClassification.CREW_PERSONAL_INFO: PermissionLevel.PRIVATE,
            DataClassification.SENSOR_RAW_DATA: PermissionLevel.PRIVATE,
            DataClassification.SECURITY_CAMERAS: PermissionLevel.PRIVATE,
            DataClassification.PASSWORDS: PermissionLevel.PRIVATE,
            DataClassification.API_KEYS: PermissionLevel.PRIVATE,
            # LEVEL 1: RESTRICTED - Essential data only, with approval
            DataClassification.CURRENT_POSITION: PermissionLevel.RESTRICTED,
            DataClassification.VESSEL_SPECIFICATIONS: PermissionLevel.RESTRICTED,
            DataClassification.ARRIVAL_TIME: PermissionLevel.RESTRICTED,
            DataClassification.CONTACT_INFO: PermissionLevel.RESTRICTED,
            # LEVEL 2: CONDITIONAL - Captain consent required
            DataClassification.WEATHER_PREFERENCES: PermissionLevel.CONDITIONAL,
            DataClassification.ROUTE_PLANNING_STYLE: PermissionLevel.CONDITIONAL,
            DataClassification.FUEL_CONSUMPTION_STATS: PermissionLevel.CONDITIONAL,
            DataClassification.MAINTENANCE_SCHEDULE: PermissionLevel.CONDITIONAL,
            # LEVEL 3: ANONYMOUS - No vessel identification
            DataClassification.POPULAR_ROUTES: PermissionLevel.ANONYMOUS,
            DataClassification.ANCHORAGE_RATINGS: PermissionLevel.ANONYMOUS,
            DataClassification.WEATHER_REPORTS: PermissionLevel.ANONYMOUS,
        }
    )

    def get_permission_level(self, data_type: DataClassification) -> PermissionLevel:
        """Get permission level for a data type"""
        return self.classification_map.get(data_type, PermissionLevel.PRIVATE)

    def can_share_automatically(self, data_type: DataClassification) -> bool:
        """Check if data can be shared without captain approval"""
        # Only anonymous data can be shared automatically
        return self.get_permission_level(data_type) == PermissionLevel.ANONYMOUS

    def requires_explicit_consent(self, data_type: DataClassification) -> bool:
        """Check if data requires explicit captain consent"""
        level = self.get_permission_level(data_type)
        return level in [PermissionLevel.PRIVATE, PermissionLevel.RESTRICTED, PermissionLevel.CONDITIONAL]

    def is_private_data(self, data_type: DataClassification) -> bool:
        """Check if data is classified as private (never share)"""
        return self.get_permission_level(data_type) == PermissionLevel.PRIVATE

    def get_sharable_data_types(self) -> List[DataClassification]:
        """Get list of data types that can potentially be shared"""
        return [data_type for data_type, level in self.classification_map.items() if level != PermissionLevel.PRIVATE]

    def validate_data_request(self, data_types: List[DataClassification]) -> Dict[str, Any]:
        """
        Validate a data sharing request
        Returns categorization of data by permission level
        """
        validation = {
            "private": [],
            "restricted": [],
            "conditional": [],
            "anonymous": [],
            "requires_approval": [],
            "auto_deny": [],
        }

        for data_type in data_types:
            level = self.get_permission_level(data_type)

            if level == PermissionLevel.PRIVATE:
                validation["private"].append(data_type)
                validation["auto_deny"].append(data_type)
            elif level == PermissionLevel.RESTRICTED:
                validation["restricted"].append(data_type)
                validation["requires_approval"].append(data_type)
            elif level == PermissionLevel.CONDITIONAL:
                validation["conditional"].append(data_type)
                validation["requires_approval"].append(data_type)
            elif level == PermissionLevel.ANONYMOUS:
                validation["anonymous"].append(data_type)

        return validation

    def get_minimal_data_for_purpose(self, purpose: str) -> List[DataClassification]:
        """
        Get minimal data set required for a specific purpose
        Implements data minimization principle
        """
        minimal_data_map = {
            "berth_reservation": [
                DataClassification.VESSEL_SPECIFICATIONS,
                DataClassification.ARRIVAL_TIME,
            ],
            "berth_assignment": [
                DataClassification.VESSEL_SPECIFICATIONS,
                DataClassification.ARRIVAL_TIME,
            ],
            "check_in": [
                DataClassification.VESSEL_SPECIFICATIONS,
                DataClassification.CURRENT_POSITION,
            ],
            "emergency": [
                DataClassification.CURRENT_POSITION,
                DataClassification.VESSEL_SPECIFICATIONS,
                DataClassification.CONTACT_INFO,
            ],
            "weather_forecast": [
                DataClassification.CURRENT_POSITION,
            ],
            "route_planning": [
                DataClassification.CURRENT_POSITION,
            ],
        }

        return minimal_data_map.get(purpose, [])

    def anonymize_data(self, data: Dict[str, Any], data_type: DataClassification) -> Dict[str, Any]:
        """
        Anonymize data for sharing
        Removes identifying information
        """
        if self.get_permission_level(data_type) == PermissionLevel.ANONYMOUS:
            # Remove all identifying fields
            anonymized = data.copy()

            # Remove common identifying fields
            for field_name in [
                "vessel_name",
                "vessel_id",
                "owner_id",
                "captain_id",
                "contact_info",
                "email",
                "phone",
                "mmsi",
            ]:
                anonymized.pop(field_name, None)

            return anonymized

        return data

    def to_dict(self) -> Dict[str, Any]:
        """Export policy configuration"""
        return {"classification_map": {k.value: v.value for k, v in self.classification_map.items()}}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataPolicy":
        """Import policy configuration"""
        classification_map = {
            DataClassification(k): PermissionLevel(v) for k, v in data.get("classification_map", {}).items()
        }
        return cls(classification_map=classification_map)


# Default policy instance
DEFAULT_DATA_POLICY = DataPolicy()


def get_default_policy() -> DataPolicy:
    """Get default data policy"""
    return DEFAULT_DATA_POLICY
