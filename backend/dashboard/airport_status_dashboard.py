"""Airport-Style Real-Time Status Dashboard for Ada Maritime AI"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from ..logger import get_logger

logger = get_logger(__name__)


@dataclass
class VesselStatus:
    """Real-time vessel status for dashboard"""
    vessel_id: str
    vessel_name: str
    vessel_type: str
    status: str
    current_gate: Optional[str]
    estimated_arrival: Optional[str]
    estimated_departure: Optional[str]
    services_required: List[str]
    services_completed: List[str]
    delay_minutes: int = 0


@dataclass
class GateStatus:
    """Real-time gate status for dashboard"""
    gate_id: str
    gate_number: str
    terminal_id: str
    status: str
    current_vessel: Optional[str]
    occupied_until: Optional[str]
    next_scheduled: Optional[str]


@dataclass
class TerminalStatus:
    """Real-time terminal status for dashboard"""
    terminal_id: str
    terminal_name: str
    total_gates: int
    available_gates: int
    occupancy_rate: float
    vessels_docked: int
    vessels_approaching: int
    current_congestion: str


@dataclass
class ServiceQueueStatus:
    """Real-time service queue status"""
    service_type: str
    queue_length: int
    vessels_in_service: int
    estimated_wait_minutes: int
    capacity_usage_percent: float


class AirportStatusDashboard:
    """
    Real-time status dashboard for airport-style port operations

    Features:
    - Live vessel tracking (like flight tracking)
    - Gate availability status
    - Terminal occupancy monitoring
    - Service queue management
    - Traffic congestion alerts
    """

    def __init__(self, db_interface=None):
        """Initialize dashboard"""
        self.db = db_interface
        self.refresh_interval_seconds = 30
        self._running = False
        self._update_task = None
        logger.info("AirportStatusDashboard initialized")

    async def get_realtime_overview(
        self,
        port_id: str,
        terminal_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get real-time overview of entire port operations

        Args:
            port_id: Port ID
            terminal_ids: Optional list of terminal IDs to filter

        Returns:
            Complete real-time status overview
        """
        logger.info(f"Generating real-time overview for port {port_id}")

        try:
            # Fetch all data in parallel
            terminal_statuses, vessel_statuses, gate_statuses, queue_statuses, traffic_data = await asyncio.gather(
                self._get_terminal_statuses(port_id, terminal_ids),
                self._get_vessel_statuses(port_id, terminal_ids),
                self._get_gate_statuses(terminal_ids),
                self._get_queue_statuses(terminal_ids),
                self._get_traffic_data(port_id),
                return_exceptions=True
            )

            # Handle exceptions
            if isinstance(terminal_statuses, Exception):
                terminal_statuses = []
            if isinstance(vessel_statuses, Exception):
                vessel_statuses = []
            if isinstance(gate_statuses, Exception):
                gate_statuses = []
            if isinstance(queue_statuses, Exception):
                queue_statuses = []
            if isinstance(traffic_data, Exception):
                traffic_data = {}

            # Calculate metrics
            metrics = self._calculate_metrics(
                terminal_statuses,
                vessel_statuses,
                gate_statuses,
                queue_statuses
            )

            return {
                "port_id": port_id,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "terminals": [asdict(t) for t in terminal_statuses],
                "vessels": [asdict(v) for v in vessel_statuses],
                "gates": [asdict(g) for g in gate_statuses],
                "service_queues": [asdict(q) for q in queue_statuses],
                "traffic": traffic_data,
                "alerts": self._generate_alerts(
                    terminal_statuses, vessel_statuses, traffic_data
                )
            }

        except Exception as e:
            logger.error(f"Error generating overview: {str(e)}")
            return {
                "port_id": port_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _get_terminal_statuses(
        self,
        port_id: str,
        terminal_ids: Optional[List[str]]
    ) -> List[TerminalStatus]:
        """Get status of all terminals"""
        if not self.db:
            return self._mock_terminal_statuses()

        terminals = await self.db.get_all_terminals(port_id)

        if terminal_ids:
            terminals = [t for t in terminals if t.terminal_id in terminal_ids]

        return [
            TerminalStatus(
                terminal_id=t.terminal_id,
                terminal_name=t.name,
                total_gates=t.total_gates,
                available_gates=t.available_gates,
                occupancy_rate=t.occupancy_rate,
                vessels_docked=t.total_gates - t.available_gates,
                vessels_approaching=0,  # Would come from tracking system
                current_congestion=self._classify_congestion(t.occupancy_rate)
            )
            for t in terminals
        ]

    async def _get_vessel_statuses(
        self,
        port_id: str,
        terminal_ids: Optional[List[str]]
    ) -> List[VesselStatus]:
        """Get status of all vessels"""
        if not self.db:
            return self._mock_vessel_statuses()

        # In production, would query vessels in port or approaching
        assignments = await self.db.get_gate_assignments(
            terminal_id=terminal_ids[0] if terminal_ids else None
        )

        vessel_statuses = []
        for assignment in assignments:
            vessel_statuses.append(
                VesselStatus(
                    vessel_id=assignment.vessel_id,
                    vessel_name=f"Vessel-{assignment.vessel_id}",
                    vessel_type="passenger",
                    status=assignment.status,
                    current_gate=assignment.gate_id,
                    estimated_arrival=assignment.scheduled_arrival.isoformat(),
                    estimated_departure=assignment.scheduled_departure.isoformat(),
                    services_required=assignment.services_required,
                    services_completed=assignment.services_completed,
                    delay_minutes=self._calculate_delay(assignment)
                )
            )

        return vessel_statuses

    async def _get_gate_statuses(
        self,
        terminal_ids: Optional[List[str]]
    ) -> List[GateStatus]:
        """Get status of all gates"""
        if not self.db:
            return self._mock_gate_statuses()

        # In production, would query all gates
        gate_statuses = []
        # Mock implementation
        return gate_statuses

    async def _get_queue_statuses(
        self,
        terminal_ids: Optional[List[str]]
    ) -> List[ServiceQueueStatus]:
        """Get status of all service queues"""
        if not self.db:
            return self._mock_queue_statuses()

        queue_statuses = []
        service_types = ["fuel", "water", "maintenance", "cleaning", "customs"]

        for service_type in service_types:
            for terminal_id in (terminal_ids or ["default"]):
                queue = await self.db.get_service_queue_status(
                    service_type, terminal_id
                )

                if queue:
                    capacity_usage = (
                        len(queue.vessels_in_service) / queue.max_concurrent_services * 100
                    )

                    queue_statuses.append(
                        ServiceQueueStatus(
                            service_type=service_type,
                            queue_length=queue.queue_length,
                            vessels_in_service=len(queue.vessels_in_service),
                            estimated_wait_minutes=queue.estimated_wait_time,
                            capacity_usage_percent=capacity_usage
                        )
                    )

        return queue_statuses

    async def _get_traffic_data(self, port_id: str) -> Dict[str, Any]:
        """Get current traffic data"""
        if not self.db:
            return self._mock_traffic_data()

        traffic = await self.db.get_current_traffic_data(port_id)

        if traffic:
            return {
                "vessels_in_port": traffic.vessels_in_port,
                "vessels_approaching": traffic.vessels_approaching,
                "vessels_departing": traffic.vessels_departing,
                "weather_condition": traffic.weather_condition,
                "congestion_level": traffic.congestion_level,
                "is_safe": traffic.is_safe_for_operations,
                "estimated_wait_minutes": traffic.estimated_wait_time_minutes
            }

        return {}

    def _calculate_metrics(
        self,
        terminals: List[TerminalStatus],
        vessels: List[VesselStatus],
        gates: List[GateStatus],
        queues: List[ServiceQueueStatus]
    ) -> Dict[str, Any]:
        """Calculate aggregate metrics"""
        total_gates = sum(t.total_gates for t in terminals)
        available_gates = sum(t.available_gates for t in terminals)

        delayed_vessels = sum(1 for v in vessels if v.delay_minutes > 0)
        on_time_rate = (
            (len(vessels) - delayed_vessels) / len(vessels) * 100
            if vessels else 100
        )

        avg_queue_wait = (
            sum(q.estimated_wait_minutes for q in queues) / len(queues)
            if queues else 0
        )

        return {
            "total_terminals": len(terminals),
            "total_gates": total_gates,
            "available_gates": available_gates,
            "overall_occupancy_rate": (
                (total_gates - available_gates) / total_gates * 100
                if total_gates > 0 else 0
            ),
            "total_vessels": len(vessels),
            "delayed_vessels": delayed_vessels,
            "on_time_rate_percent": on_time_rate,
            "avg_queue_wait_minutes": avg_queue_wait,
            "total_service_queues": len(queues)
        }

    def _generate_alerts(
        self,
        terminals: List[TerminalStatus],
        vessels: List[VesselStatus],
        traffic: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate real-time alerts"""
        alerts = []

        # High occupancy alerts
        for terminal in terminals:
            if terminal.occupancy_rate > 90:
                alerts.append({
                    "severity": "high",
                    "type": "high_occupancy",
                    "message": f"Terminal {terminal.terminal_name} at {terminal.occupancy_rate:.0f}% capacity",
                    "terminal_id": terminal.terminal_id
                })

        # Delay alerts
        critical_delays = [v for v in vessels if v.delay_minutes > 30]
        if critical_delays:
            alerts.append({
                "severity": "medium",
                "type": "delays",
                "message": f"{len(critical_delays)} vessels delayed >30 minutes"
            })

        # Weather alerts
        if traffic and not traffic.get("is_safe", True):
            alerts.append({
                "severity": "critical",
                "type": "weather",
                "message": f"Unsafe weather conditions: {traffic.get('weather_condition', 'unknown')}"
            })

        return alerts

    def _classify_congestion(self, occupancy_rate: float) -> str:
        """Classify congestion level"""
        if occupancy_rate < 50:
            return "low"
        elif occupancy_rate < 75:
            return "medium"
        elif occupancy_rate < 90:
            return "high"
        else:
            return "critical"

    def _calculate_delay(self, assignment) -> int:
        """Calculate delay in minutes"""
        if assignment.actual_arrival and assignment.scheduled_arrival:
            delta = assignment.actual_arrival - assignment.scheduled_arrival
            return max(0, int(delta.total_seconds() / 60))
        return 0

    # Mock data methods for testing
    def _mock_terminal_statuses(self) -> List[TerminalStatus]:
        """Mock terminal statuses"""
        return [
            TerminalStatus(
                terminal_id="TERM-A",
                terminal_name="Terminal A - International",
                total_gates=20,
                available_gates=8,
                occupancy_rate=60.0,
                vessels_docked=12,
                vessels_approaching=3,
                current_congestion="medium"
            ),
            TerminalStatus(
                terminal_id="TERM-B",
                terminal_name="Terminal B - Domestic",
                total_gates=15,
                available_gates=5,
                occupancy_rate=66.7,
                vessels_docked=10,
                vessels_approaching=2,
                current_congestion="medium"
            )
        ]

    def _mock_vessel_statuses(self) -> List[VesselStatus]:
        """Mock vessel statuses"""
        now = datetime.now()
        return [
            VesselStatus(
                vessel_id="V001",
                vessel_name="Sea Star",
                vessel_type="passenger",
                status="docked",
                current_gate="A-01",
                estimated_arrival=(now - timedelta(hours=1)).isoformat(),
                estimated_departure=(now + timedelta(hours=2)).isoformat(),
                services_required=["fuel", "water", "cleaning"],
                services_completed=["fuel"],
                delay_minutes=0
            ),
            VesselStatus(
                vessel_id="V002",
                vessel_name="Ocean Queen",
                vessel_type="passenger",
                status="approaching",
                current_gate=None,
                estimated_arrival=(now + timedelta(minutes=30)).isoformat(),
                estimated_departure=(now + timedelta(hours=4)).isoformat(),
                services_required=["fuel", "maintenance"],
                services_completed=[],
                delay_minutes=15
            )
        ]

    def _mock_gate_statuses(self) -> List[GateStatus]:
        """Mock gate statuses"""
        now = datetime.now()
        return [
            GateStatus(
                gate_id="A-01",
                gate_number="01",
                terminal_id="TERM-A",
                status="occupied",
                current_vessel="V001",
                occupied_until=(now + timedelta(hours=2)).isoformat(),
                next_scheduled=(now + timedelta(hours=3)).isoformat()
            ),
            GateStatus(
                gate_id="A-02",
                gate_number="02",
                terminal_id="TERM-A",
                status="available",
                current_vessel=None,
                occupied_until=None,
                next_scheduled=(now + timedelta(minutes=30)).isoformat()
            )
        ]

    def _mock_queue_statuses(self) -> List[ServiceQueueStatus]:
        """Mock queue statuses"""
        return [
            ServiceQueueStatus(
                service_type="fuel",
                queue_length=3,
                vessels_in_service=2,
                estimated_wait_minutes=45,
                capacity_usage_percent=66.7
            ),
            ServiceQueueStatus(
                service_type="maintenance",
                queue_length=1,
                vessels_in_service=1,
                estimated_wait_minutes=30,
                capacity_usage_percent=33.3
            )
        ]

    def _mock_traffic_data(self) -> Dict[str, Any]:
        """Mock traffic data"""
        return {
            "vessels_in_port": 22,
            "vessels_approaching": 5,
            "vessels_departing": 3,
            "weather_condition": "clear",
            "congestion_level": "medium",
            "is_safe": True,
            "estimated_wait_minutes": 20
        }

    async def start_live_monitoring(self, port_id: str, callback=None):
        """Start live monitoring with periodic updates"""
        self._running = True
        logger.info(f"Starting live monitoring for port {port_id}")

        while self._running:
            try:
                overview = await self.get_realtime_overview(port_id)

                if callback:
                    await callback(overview)

                await asyncio.sleep(self.refresh_interval_seconds)

            except Exception as e:
                logger.error(f"Error in live monitoring: {str(e)}")
                await asyncio.sleep(self.refresh_interval_seconds)

    def stop_live_monitoring(self):
        """Stop live monitoring"""
        self._running = False
        logger.info("Stopped live monitoring")
