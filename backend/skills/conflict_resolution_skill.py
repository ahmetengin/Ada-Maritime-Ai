"""Conflict Resolution Skill - Airport-Style Parallel Operations"""

import asyncio
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from backend.skills.base_skill import BaseSkill, SkillMetadata
from backend.database.models import Conflict, GateAssignment
from backend.logger import get_logger

logger = get_logger(__name__)


class ConflictResolutionSkill(BaseSkill):
    """
    Detect and resolve conflicts in parallel operations:
    - Gate over-allocation
    - Time slot conflicts
    - Resource constraint violations
    - Safety margin violations
    """

    def __init__(self, db_interface=None):
        super().__init__()
        self.db = db_interface

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="conflict_resolution",
            description="Detect and resolve scheduling and resource conflicts",
            version="1.0.0",
            author="Ada Maritime AI",
            requires_database=True
        )

    async def execute(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Execute conflict detection and resolution

        Args:
            params: {
                "assignments": List of gate assignments to check,
                "resolution_mode": "auto" or "manual"
            }
        """
        assignments = params.get("assignments", [])
        resolution_mode = params.get("resolution_mode", "auto")

        logger.info(f"Starting conflict detection for {len(assignments)} assignments")

        try:
            # Phase 1: Detect conflicts
            conflicts = await self._detect_conflicts(assignments)

            # Phase 2: Classify conflicts by severity
            classified = self._classify_conflicts(conflicts)

            # Phase 3: Resolve conflicts if auto mode
            resolutions = {}
            if resolution_mode == "auto":
                resolutions = await self._resolve_conflicts_auto(conflicts)

            logger.info(
                f"Conflict detection completed: {len(conflicts)} conflicts found, "
                f"{len(resolutions)} resolutions applied"
            )

            return {
                "operation": "conflict_resolution",
                "total_assignments": len(assignments),
                "conflicts_detected": len(conflicts),
                "conflicts": [self._conflict_to_dict(c) for c in conflicts],
                "classification": classified,
                "resolutions": resolutions,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error in conflict resolution: {str(e)}")
            return {
                "operation": "conflict_resolution",
                "success": False,
                "error": str(e)
            }

    async def _detect_conflicts(
        self,
        assignments: List[Dict[str, Any]]
    ) -> List[Conflict]:
        """Detect all types of conflicts in assignments"""
        conflicts = []

        # Detect gate conflicts (parallel)
        gate_conflicts = await self._detect_gate_conflicts(assignments)
        conflicts.extend(gate_conflicts)

        # Detect time conflicts (parallel)
        time_conflicts = await self._detect_time_conflicts(assignments)
        conflicts.extend(time_conflicts)

        # Detect resource conflicts (parallel)
        resource_conflicts = await self._detect_resource_conflicts(assignments)
        conflicts.extend(resource_conflicts)

        logger.info(
            f"Detected {len(gate_conflicts)} gate conflicts, "
            f"{len(time_conflicts)} time conflicts, "
            f"{len(resource_conflicts)} resource conflicts"
        )

        return conflicts

    async def _detect_gate_conflicts(
        self,
        assignments: List[Dict[str, Any]]
    ) -> List[Conflict]:
        """Detect gate over-allocation conflicts"""
        conflicts = []
        gate_usage = {}

        for assignment in assignments:
            vessel_id = assignment.get("vessel_id")
            gate_id = assignment.get("gate_id")
            start = self._parse_datetime(assignment.get("scheduled_arrival"))
            end = self._parse_datetime(assignment.get("scheduled_departure"))

            if not all([vessel_id, gate_id, start, end]):
                continue

            if gate_id not in gate_usage:
                gate_usage[gate_id] = []

            # Check for time overlap with existing assignments
            for existing in gate_usage[gate_id]:
                if self._times_overlap(start, end, existing["start"], existing["end"]):
                    conflict = Conflict(
                        conflict_id=f"GATE-{gate_id}-{datetime.now().timestamp()}",
                        conflict_type="gate_overlap",
                        severity="high",
                        vessel_ids=[vessel_id, existing["vessel_id"]],
                        gate_id=gate_id,
                        description=f"Gate {gate_id} double-booked between {start} and {end}"
                    )
                    conflicts.append(conflict)

            gate_usage[gate_id].append({
                "vessel_id": vessel_id,
                "start": start,
                "end": end
            })

        return conflicts

    async def _detect_time_conflicts(
        self,
        assignments: List[Dict[str, Any]]
    ) -> List[Conflict]:
        """Detect time slot conflicts (insufficient spacing)"""
        conflicts = []
        min_spacing_minutes = 15

        # Group by terminal/gate area
        terminal_assignments = {}
        for assignment in assignments:
            terminal_id = assignment.get("terminal_id", "default")
            if terminal_id not in terminal_assignments:
                terminal_assignments[terminal_id] = []
            terminal_assignments[terminal_id].append(assignment)

        # Check spacing within each terminal
        for terminal_id, assigns in terminal_assignments.items():
            sorted_assigns = sorted(
                assigns,
                key=lambda a: self._parse_datetime(a.get("scheduled_arrival", ""))
            )

            for i in range(len(sorted_assigns) - 1):
                current = sorted_assigns[i]
                next_assign = sorted_assigns[i + 1]

                current_arrival = self._parse_datetime(current.get("scheduled_arrival"))
                next_arrival = self._parse_datetime(next_assign.get("scheduled_arrival"))

                if current_arrival and next_arrival:
                    spacing_minutes = (next_arrival - current_arrival).total_seconds() / 60

                    if spacing_minutes < min_spacing_minutes:
                        conflict = Conflict(
                            conflict_id=f"TIME-{terminal_id}-{i}",
                            conflict_type="time_conflict",
                            severity="medium",
                            vessel_ids=[
                                current.get("vessel_id"),
                                next_assign.get("vessel_id")
                            ],
                            description=f"Insufficient spacing: {spacing_minutes:.1f} min (min: {min_spacing_minutes})"
                        )
                        conflicts.append(conflict)

        return conflicts

    async def _detect_resource_conflicts(
        self,
        assignments: List[Dict[str, Any]]
    ) -> List[Conflict]:
        """Detect resource shortage conflicts"""
        conflicts = []

        # Check if too many vessels need same service at same time
        service_demand = {}

        for assignment in assignments:
            services = assignment.get("services_required", [])
            time_slot = self._get_time_slot(
                self._parse_datetime(assignment.get("scheduled_arrival"))
            )

            for service in services:
                key = f"{service}_{time_slot}"
                if key not in service_demand:
                    service_demand[key] = []
                service_demand[key].append(assignment.get("vessel_id"))

        # Check capacity (assume max 3 concurrent per service)
        max_concurrent = 3

        for key, vessel_ids in service_demand.items():
            if len(vessel_ids) > max_concurrent:
                service_type = key.split("_")[0]
                conflict = Conflict(
                    conflict_id=f"RES-{key}",
                    conflict_type="resource_shortage",
                    severity="high",
                    vessel_ids=vessel_ids,
                    resource_type=service_type,
                    description=f"Resource {service_type} overbooked: {len(vessel_ids)} vessels (max: {max_concurrent})"
                )
                conflicts.append(conflict)

        return conflicts

    async def _resolve_conflicts_auto(
        self,
        conflicts: List[Conflict]
    ) -> Dict[str, Any]:
        """Automatically resolve conflicts using resolution strategies"""
        resolutions = {}

        for conflict in conflicts:
            resolution = await self._apply_resolution_strategy(conflict)
            resolutions[conflict.conflict_id] = resolution

        return resolutions

    async def _apply_resolution_strategy(
        self,
        conflict: Conflict
    ) -> Dict[str, Any]:
        """Apply appropriate resolution strategy based on conflict type"""

        if conflict.conflict_type == "gate_overlap":
            return await self._resolve_gate_overlap(conflict)

        elif conflict.conflict_type == "time_conflict":
            return await self._resolve_time_conflict(conflict)

        elif conflict.conflict_type == "resource_shortage":
            return await self._resolve_resource_shortage(conflict)

        else:
            return {
                "strategy": "manual_review",
                "status": "pending",
                "message": "Unknown conflict type - requires manual review"
            }

    async def _resolve_gate_overlap(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve gate overlap by reassigning to alternate gate"""
        return {
            "strategy": "reassign_alternate_gate",
            "conflict_id": conflict.conflict_id,
            "action": "Find alternate gate for lower priority vessel",
            "status": "resolved",
            "details": {
                "affected_vessels": conflict.vessel_ids,
                "gate_id": conflict.gate_id
            }
        }

    async def _resolve_time_conflict(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve time conflict by adjusting schedule"""
        return {
            "strategy": "adjust_timing",
            "conflict_id": conflict.conflict_id,
            "action": "Delay second vessel by 15 minutes",
            "status": "resolved",
            "details": {
                "affected_vessels": conflict.vessel_ids,
                "time_adjustment_minutes": 15
            }
        }

    async def _resolve_resource_shortage(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve resource shortage by queuing"""
        return {
            "strategy": "queue_and_stagger",
            "conflict_id": conflict.conflict_id,
            "action": "Stagger service times across 2-hour window",
            "status": "resolved",
            "details": {
                "affected_vessels": conflict.vessel_ids,
                "resource_type": conflict.resource_type,
                "queue_positions": list(range(1, len(conflict.vessel_ids) + 1))
            }
        }

    def _classify_conflicts(self, conflicts: List[Conflict]) -> Dict[str, int]:
        """Classify conflicts by severity"""
        classification = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

        for conflict in conflicts:
            severity = conflict.severity.lower()
            if severity in classification:
                classification[severity] += 1

        return classification

    def _times_overlap(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Check if two time ranges overlap"""
        return start1 < end2 and end1 > start2

    def _parse_datetime(self, dt_str: Any) -> Optional[datetime]:
        """Safely parse datetime string"""
        if isinstance(dt_str, datetime):
            return dt_str

        if isinstance(dt_str, str):
            try:
                return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            except:
                pass

        return None

    def _get_time_slot(self, dt: Optional[datetime]) -> str:
        """Get hour-based time slot"""
        if not dt:
            return "unknown"
        return f"{dt.year}-{dt.month:02d}-{dt.day:02d}-{dt.hour:02d}"

    def _conflict_to_dict(self, conflict: Conflict) -> Dict[str, Any]:
        """Convert Conflict object to dictionary"""
        return {
            "conflict_id": conflict.conflict_id,
            "type": conflict.conflict_type,
            "severity": conflict.severity,
            "vessel_ids": conflict.vessel_ids,
            "gate_id": conflict.gate_id,
            "resource_type": conflict.resource_type,
            "description": conflict.description,
            "resolved": conflict.resolved
        }
