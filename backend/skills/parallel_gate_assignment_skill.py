"""Parallel Gate Assignment Skill - Airport-Style Operations"""

import asyncio
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from backend.skills.base_skill import BaseSkill, SkillMetadata
from backend.database.models import Vessel, Gate, GateAssignment, VesselStatus, GateStatus
from backend.logger import get_logger

logger = get_logger(__name__)


class ParallelGateAssignmentSkill(BaseSkill):
    """
    Assign multiple vessels to gates simultaneously using parallel processing.
    Uses conflict detection and optimization algorithms.
    """

    def __init__(self, db_interface=None):
        super().__init__()
        self.db = db_interface
        self.assignment_lock = asyncio.Lock()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="parallel_gate_assignment",
            description="Assign multiple vessels to gates in parallel with conflict detection",
            version="1.0.0",
            author="Ada Maritime AI",
            requires_database=True
        )

    async def execute(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Execute parallel gate assignments

        Args:
            params: {
                "vessel_ids": List[str],
                "terminal_id": str,
                "time_window": {"start": datetime, "end": datetime}
            }
        """
        self.validate_params(params, ["vessel_ids"])

        vessel_ids = params.get("vessel_ids", [])
        terminal_id = params.get("terminal_id")
        time_window = params.get("time_window")

        logger.info(f"Starting parallel gate assignment for {len(vessel_ids)} vessels")

        try:
            # Phase 1: Load vessel data in parallel
            vessels = await self._load_vessels_parallel(vessel_ids)

            # Phase 2: Find candidate gates for each vessel in parallel
            candidates = await self._find_candidate_gates_parallel(
                vessels, terminal_id, time_window
            )

            # Phase 3: Optimize assignments (sequential bottleneck)
            assignments = await self._optimize_assignments(vessels, candidates)

            # Phase 4: Allocate gates atomically in parallel
            results = await self._allocate_gates_parallel(assignments)

            # Phase 5: Create assignment records
            assignment_records = await self._create_assignment_records(
                assignments, results
            )

            successful = sum(1 for r in results if r.get("success", False))
            failed = len(results) - successful

            logger.info(
                f"Gate assignment completed: {successful} successful, {failed} failed"
            )

            return {
                "operation": "parallel_gate_assignment",
                "total_vessels": len(vessel_ids),
                "assigned": successful,
                "failed": failed,
                "assignments": assignment_records,
                "success": successful > 0
            }

        except Exception as e:
            logger.error(f"Error in parallel gate assignment: {str(e)}")
            return {
                "operation": "parallel_gate_assignment",
                "success": False,
                "error": str(e)
            }

    async def _load_vessels_parallel(self, vessel_ids: List[str]) -> List[Vessel]:
        """Load multiple vessels in parallel"""
        if not self.db:
            return []

        tasks = [self.db.get_vessel(vid) for vid in vessel_ids]
        vessels = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and None values
        valid_vessels = [
            v for v in vessels
            if v is not None and not isinstance(v, Exception)
        ]

        logger.info(f"Loaded {len(valid_vessels)} vessels from {len(vessel_ids)} IDs")
        return valid_vessels

    async def _find_candidate_gates_parallel(
        self,
        vessels: List[Vessel],
        terminal_id: Optional[str],
        time_window: Optional[Dict]
    ) -> Dict[str, List[Gate]]:
        """Find candidate gates for each vessel in parallel"""
        if not self.db:
            return {}

        tasks = [
            self.db.search_suitable_gates(vessel, terminal_id, time_window)
            for vessel in vessels
        ]

        candidates_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Map vessel_id to candidate gates
        candidates = {}
        for vessel, gates in zip(vessels, candidates_list):
            if not isinstance(gates, Exception):
                candidates[vessel.vessel_id] = gates
            else:
                logger.warning(
                    f"Failed to find gates for vessel {vessel.vessel_id}: {gates}"
                )
                candidates[vessel.vessel_id] = []

        return candidates

    async def _optimize_assignments(
        self,
        vessels: List[Vessel],
        candidates: Dict[str, List[Gate]]
    ) -> List[Tuple[str, str]]:
        """
        Optimize gate assignments using greedy algorithm with priority
        Returns list of (vessel_id, gate_id) tuples
        """
        assignments = []
        assigned_gates = set()

        # Sort vessels by priority (higher priority first)
        sorted_vessels = sorted(
            vessels,
            key=lambda v: (v.priority_level, -v.length_meters),
            reverse=True
        )

        for vessel in sorted_vessels:
            available_gates = [
                gate for gate in candidates.get(vessel.vessel_id, [])
                if gate.gate_id not in assigned_gates
            ]

            if not available_gates:
                logger.warning(f"No available gates for vessel {vessel.vessel_id}")
                continue

            # Choose best gate based on size match and cost
            best_gate = min(
                available_gates,
                key=lambda g: (
                    abs(g.length_meters - vessel.length_meters),
                    g.hourly_rate_eur
                )
            )

            assignments.append((vessel.vessel_id, best_gate.gate_id))
            assigned_gates.add(best_gate.gate_id)

        logger.info(f"Optimized {len(assignments)} assignments")
        return assignments

    async def _allocate_gates_parallel(
        self,
        assignments: List[Tuple[str, str]]
    ) -> List[Dict[str, Any]]:
        """Allocate gates atomically in parallel"""
        if not self.db:
            return []

        async with self.assignment_lock:
            tasks = [
                self.db.allocate_gate(vessel_id, gate_id)
                for vessel_id, gate_id in assignments
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert results to dicts
        allocation_results = []
        for (vessel_id, gate_id), result in zip(assignments, results):
            if isinstance(result, Exception):
                allocation_results.append({
                    "vessel_id": vessel_id,
                    "gate_id": gate_id,
                    "success": False,
                    "error": str(result)
                })
            else:
                allocation_results.append({
                    "vessel_id": vessel_id,
                    "gate_id": gate_id,
                    "success": result
                })

        return allocation_results

    async def _create_assignment_records(
        self,
        assignments: List[Tuple[str, str]],
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create assignment records for successful allocations"""
        records = []

        for result in results:
            if result.get("success", False):
                records.append({
                    "assignment_id": f"ASG-{result['vessel_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "vessel_id": result["vessel_id"],
                    "gate_id": result["gate_id"],
                    "status": "assigned",
                    "timestamp": datetime.now().isoformat()
                })

        return records
