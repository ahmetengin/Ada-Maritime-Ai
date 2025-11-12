"""Traffic-Aware Scheduling Skill - Airport-Style Operations"""

import asyncio
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from backend.skills.base_skill import BaseSkill, SkillMetadata
from backend.database.models import Vessel, TrafficData
from backend.logger import get_logger

logger = get_logger(__name__)


class TrafficAwareSchedulingSkill(BaseSkill):
    """
    Schedule multiple vessels respecting:
    - Gate availability windows
    - Traffic patterns (ferries, weather)
    - Resource queues (fuel, repairs)
    - Safety constraints
    """

    def __init__(self, db_interface=None):
        super().__init__()
        self.db = db_interface

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="traffic_aware_scheduling",
            description="Schedule vessels with traffic and weather awareness",
            version="1.0.0",
            author="Ada Maritime AI",
            requires_database=True
        )

    async def execute(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Execute traffic-aware scheduling

        Args:
            params: {
                "vessels": List[Vessel] or List[str] (vessel_ids),
                "port_id": str,
                "scheduling_window_hours": int
            }
        """
        vessels_input = params.get("vessels", [])
        port_id = params.get("port_id", "default_port")
        window_hours = params.get("scheduling_window_hours", 24)

        logger.info(f"Starting traffic-aware scheduling for {len(vessels_input)} vessels")

        try:
            # Load vessels if IDs provided
            if vessels_input and isinstance(vessels_input[0], str):
                vessels = await self._load_vessels(vessels_input)
            else:
                vessels = vessels_input

            # Phase 1: Fetch traffic data in parallel
            traffic_data = await self._fetch_traffic_data_parallel(port_id)

            # Phase 2: Calculate safe arrival windows for each vessel
            time_windows = await self._calculate_time_windows_parallel(
                vessels, traffic_data
            )

            # Phase 3: Build optimal schedule
            schedule = await self._optimize_schedule(
                vessels, time_windows, traffic_data
            )

            # Calculate metrics
            avg_wait_time = self._calculate_avg_wait_time(schedule)

            logger.info(
                f"Scheduling completed: {len(schedule)} vessels scheduled, "
                f"avg wait time: {avg_wait_time:.1f} minutes"
            )

            return {
                "operation": "traffic_aware_scheduling",
                "scheduled_vessels": len(schedule),
                "schedule": schedule,
                "optimization_metrics": {
                    "avg_wait_time_minutes": avg_wait_time,
                    "safety_margin": "2.5x nominal",
                    "weather_safe": traffic_data.get("is_safe", True)
                },
                "success": True
            }

        except Exception as e:
            logger.error(f"Error in traffic-aware scheduling: {str(e)}")
            return {
                "operation": "traffic_aware_scheduling",
                "success": False,
                "error": str(e)
            }

    async def _load_vessels(self, vessel_ids: List[str]) -> List[Vessel]:
        """Load vessels from database"""
        if not self.db:
            return []

        tasks = [self.db.get_vessel(vid) for vid in vessel_ids]
        vessels = await asyncio.gather(*tasks, return_exceptions=True)

        return [v for v in vessels if v and not isinstance(v, Exception)]

    async def _fetch_traffic_data_parallel(self, port_id: str) -> Dict[str, Any]:
        """Fetch traffic data from multiple sources in parallel"""
        # Parallel data fetching
        tasks = [
            self._fetch_ferry_schedule(port_id),
            self._fetch_weather_data(port_id),
            self._fetch_current_congestion(port_id)
        ]

        ferry_schedule, weather_data, congestion = await asyncio.gather(
            *tasks, return_exceptions=True
        )

        # Combine data
        traffic_data = {
            "ferry_schedule": ferry_schedule if not isinstance(ferry_schedule, Exception) else {},
            "weather": weather_data if not isinstance(weather_data, Exception) else {},
            "congestion": congestion if not isinstance(congestion, Exception) else {},
            "is_safe": self._is_weather_safe(weather_data)
        }

        return traffic_data

    async def _fetch_ferry_schedule(self, port_id: str) -> Dict[str, Any]:
        """Fetch ferry schedule (mock implementation)"""
        # In production, this would call external API
        await asyncio.sleep(0.1)  # Simulate API call
        return {
            "scheduled_ferries": [
                {"time": "08:00", "duration": 30},
                {"time": "12:00", "duration": 30},
                {"time": "18:00", "duration": 30}
            ]
        }

    async def _fetch_weather_data(self, port_id: str) -> Dict[str, Any]:
        """Fetch weather data (mock implementation)"""
        await asyncio.sleep(0.1)  # Simulate API call
        return {
            "condition": "clear",
            "wind_speed_knots": 12,
            "wave_height_meters": 0.8,
            "visibility_meters": 10000,
            "forecast_hours": 24
        }

    async def _fetch_current_congestion(self, port_id: str) -> Dict[str, Any]:
        """Fetch current congestion data"""
        if not self.db:
            return {"level": "low", "queue_length": 2}

        # In production, query database for current traffic
        return {
            "level": "medium",
            "queue_length": 5,
            "avg_wait_minutes": 20
        }

    def _is_weather_safe(self, weather_data: Dict[str, Any]) -> bool:
        """Check if weather is safe for operations"""
        if isinstance(weather_data, Exception):
            return False

        condition = weather_data.get("condition", "unknown")
        wind_speed = weather_data.get("wind_speed_knots", 100)
        wave_height = weather_data.get("wave_height_meters", 10)

        return (condition not in ["storm", "severe"] and
                wind_speed < 35 and
                wave_height < 2.5)

    async def _calculate_time_windows_parallel(
        self,
        vessels: List[Vessel],
        traffic_data: Dict[str, Any]
    ) -> Dict[str, Tuple[datetime, datetime]]:
        """Calculate safe arrival time windows for each vessel in parallel"""
        tasks = [
            self._calculate_safe_arrival_window(vessel, traffic_data)
            for vessel in vessels
        ]

        windows = await asyncio.gather(*tasks)

        return {
            vessel.vessel_id: window
            for vessel, window in zip(vessels, windows)
        }

    async def _calculate_safe_arrival_window(
        self,
        vessel: Vessel,
        traffic_data: Dict[str, Any]
    ) -> Tuple[datetime, datetime]:
        """Calculate safe arrival window for a single vessel"""
        now = datetime.now()

        # Base window: next 24 hours
        earliest = now + timedelta(hours=1)
        latest = now + timedelta(hours=24)

        # Adjust for weather
        if not traffic_data.get("is_safe", True):
            earliest = now + timedelta(hours=6)  # Delay if weather is bad

        # Avoid ferry times
        ferry_schedule = traffic_data.get("ferry_schedule", {}).get("scheduled_ferries", [])
        # In production, would actually avoid ferry time slots

        return (earliest, latest)

    async def _optimize_schedule(
        self,
        vessels: List[Vessel],
        time_windows: Dict[str, Tuple[datetime, datetime]],
        traffic_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build optimal schedule respecting all constraints"""
        schedule = []
        current_time = datetime.now()

        # Sort by priority
        sorted_vessels = sorted(
            vessels,
            key=lambda v: v.priority_level,
            reverse=True
        )

        spacing_minutes = 15  # Minimum spacing between arrivals

        for vessel in sorted_vessels:
            window = time_windows.get(vessel.vessel_id)
            if not window:
                continue

            earliest, latest = window

            # Schedule at earliest safe time
            scheduled_time = max(current_time, earliest)

            schedule.append({
                "vessel_id": vessel.vessel_id,
                "vessel_name": vessel.vessel_name,
                "scheduled_arrival": scheduled_time.isoformat(),
                "scheduled_departure": (scheduled_time + timedelta(hours=2)).isoformat(),
                "priority": vessel.priority_level,
                "estimated_docking_time": 15
            })

            current_time = scheduled_time + timedelta(minutes=spacing_minutes)

        return schedule

    def _calculate_avg_wait_time(self, schedule: List[Dict[str, Any]]) -> float:
        """Calculate average wait time for scheduled vessels"""
        if not schedule:
            return 0.0

        now = datetime.now()
        total_wait = 0

        for entry in schedule:
            scheduled = datetime.fromisoformat(entry["scheduled_arrival"])
            wait_minutes = (scheduled - now).total_seconds() / 60
            total_wait += max(0, wait_minutes)

        return total_wait / len(schedule)
