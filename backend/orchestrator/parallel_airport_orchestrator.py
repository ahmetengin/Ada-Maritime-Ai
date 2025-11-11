"""Parallel Airport-Style Orchestrator for Ada Maritime AI"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .big5_orchestrator import Big5Orchestrator, SkillResult, AgentContext
from ..logger import get_logger
from ..exceptions import OrchestratorError

logger = get_logger(__name__)


@dataclass
class BatchResult:
    """Result from batch processing"""
    total_requests: int
    successful: int
    failed: int
    results: List[SkillResult]
    total_duration: float
    throughput: float  # requests per second
    timestamp: str


class ParallelAirportOrchestrator(Big5Orchestrator):
    """
    Enhanced orchestrator with parallel execution capabilities for
    airport-style operations.

    Features:
    - Batch request processing
    - Parallel skill execution
    - Conflict detection and resolution
    - Real-time status tracking
    """

    def __init__(self, api_key: Optional[str] = None, max_parallel: int = 10):
        """
        Initialize parallel orchestrator

        Args:
            api_key: Anthropic API key
            max_parallel: Maximum parallel operations (default: 10)
        """
        super().__init__(api_key)
        self.max_parallel = max_parallel
        self.semaphore = asyncio.Semaphore(max_parallel)
        logger.info(
            f"ParallelAirportOrchestrator initialized with "
            f"max_parallel={max_parallel}"
        )

    async def handle_batch_request(
        self,
        requests: List[Dict[str, Any]],
        context: AgentContext
    ) -> BatchResult:
        """
        Process multiple requests in parallel

        Args:
            requests: List of request dictionaries
            context: Agent context

        Returns:
            BatchResult with aggregated results
        """
        logger.info(f"Starting batch processing of {len(requests)} requests")
        start_time = time.time()

        try:
            # Phase 1: Process requests with semaphore control
            tasks = [
                self._process_single_request(req, context)
                for req in requests
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Phase 2: Separate successful and failed results
            skill_results = []
            for result in results:
                if isinstance(result, Exception):
                    skill_results.append(
                        SkillResult(
                            skill_name="unknown",
                            success=False,
                            data=None,
                            execution_time=0.0,
                            timestamp=datetime.now().isoformat(),
                            error=str(result)
                        )
                    )
                elif isinstance(result, SkillResult):
                    skill_results.append(result)
                else:
                    # Result from skill execution
                    skill_results.append(result)

            # Calculate metrics
            total_duration = time.time() - start_time
            successful = sum(1 for r in skill_results if r.success)
            failed = len(skill_results) - successful
            throughput = len(requests) / total_duration if total_duration > 0 else 0

            batch_result = BatchResult(
                total_requests=len(requests),
                successful=successful,
                failed=failed,
                results=skill_results,
                total_duration=total_duration,
                throughput=throughput,
                timestamp=datetime.now().isoformat()
            )

            logger.info(
                f"Batch processing completed: {successful} successful, "
                f"{failed} failed, {throughput:.2f} req/s"
            )

            return batch_result

        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise OrchestratorError(f"Batch processing failed: {str(e)}")

    async def _process_single_request(
        self,
        request: Dict[str, Any],
        context: AgentContext
    ) -> SkillResult:
        """Process a single request with semaphore control"""
        async with self.semaphore:
            skill_name = request.get("skill_name")
            params = request.get("params", {})

            if not skill_name:
                return SkillResult(
                    skill_name="unknown",
                    success=False,
                    data=None,
                    execution_time=0.0,
                    timestamp=datetime.now().isoformat(),
                    error="Missing skill_name in request"
                )

            return await self.execute_skill(skill_name, params, context)

    async def parallel_gate_assignment(
        self,
        vessel_ids: List[str],
        terminal_id: Optional[str],
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Assign multiple vessels to gates in parallel

        Args:
            vessel_ids: List of vessel IDs
            terminal_id: Terminal ID (optional)
            context: Agent context

        Returns:
            Assignment results
        """
        logger.info(
            f"Starting parallel gate assignment for {len(vessel_ids)} vessels"
        )

        # Execute gate assignment skill
        result = await self.execute_skill(
            skill_name="parallel_gate_assignment",
            params={
                "vessel_ids": vessel_ids,
                "terminal_id": terminal_id
            },
            context=context
        )

        return asdict(result)

    async def schedule_with_traffic_awareness(
        self,
        vessel_ids: List[str],
        port_id: str,
        window_hours: int,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Schedule vessels with traffic and weather awareness

        Args:
            vessel_ids: List of vessel IDs
            port_id: Port ID
            window_hours: Scheduling window in hours
            context: Agent context

        Returns:
            Schedule results
        """
        logger.info(
            f"Starting traffic-aware scheduling for {len(vessel_ids)} vessels"
        )

        result = await self.execute_skill(
            skill_name="traffic_aware_scheduling",
            params={
                "vessels": vessel_ids,
                "port_id": port_id,
                "scheduling_window_hours": window_hours
            },
            context=context
        )

        return asdict(result)

    async def allocate_resources_batch(
        self,
        allocations: List[Dict[str, Any]],
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Allocate resources to multiple vessels in parallel

        Args:
            allocations: List of {vessel_id, resources} dicts
            context: Agent context

        Returns:
            Allocation results
        """
        logger.info(
            f"Starting batch resource allocation for {len(allocations)} vessels"
        )

        result = await self.execute_skill(
            skill_name="batch_resource_allocation",
            params={"allocations": allocations},
            context=context
        )

        return asdict(result)

    async def detect_and_resolve_conflicts(
        self,
        assignments: List[Dict[str, Any]],
        resolution_mode: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Detect and optionally resolve conflicts in assignments

        Args:
            assignments: List of gate assignments
            resolution_mode: "auto" or "manual"
            context: Agent context

        Returns:
            Conflict detection and resolution results
        """
        logger.info(
            f"Starting conflict detection for {len(assignments)} assignments"
        )

        result = await self.execute_skill(
            skill_name="conflict_resolution",
            params={
                "assignments": assignments,
                "resolution_mode": resolution_mode
            },
            context=context
        )

        return asdict(result)

    async def orchestrate_full_parallel_workflow(
        self,
        vessel_ids: List[str],
        terminal_id: str,
        port_id: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Orchestrate complete parallel workflow:
        1. Schedule vessels with traffic awareness
        2. Assign gates in parallel
        3. Detect and resolve conflicts
        4. Allocate resources

        Args:
            vessel_ids: List of vessel IDs
            terminal_id: Terminal ID
            port_id: Port ID
            context: Agent context

        Returns:
            Complete workflow results
        """
        logger.info(
            f"Starting full parallel workflow for {len(vessel_ids)} vessels"
        )
        workflow_start = time.time()

        try:
            # Phase 1: Traffic-aware scheduling
            schedule_result = await self.schedule_with_traffic_awareness(
                vessel_ids=vessel_ids,
                port_id=port_id,
                window_hours=24,
                context=context
            )

            # Phase 2: Parallel gate assignment
            assignment_result = await self.parallel_gate_assignment(
                vessel_ids=vessel_ids,
                terminal_id=terminal_id,
                context=context
            )

            assignments = assignment_result.get("data", {}).get("assignments", [])

            # Phase 3: Conflict detection and resolution
            conflict_result = await self.detect_and_resolve_conflicts(
                assignments=assignments,
                resolution_mode="auto",
                context=context
            )

            # Phase 4: Resource allocation
            resource_allocations = [
                {
                    "vessel_id": vid,
                    "resources": ["fuel", "water", "cleaning"]
                }
                for vid in vessel_ids
            ]

            resource_result = await self.allocate_resources_batch(
                allocations=resource_allocations,
                context=context
            )

            workflow_duration = time.time() - workflow_start

            logger.info(
                f"Full parallel workflow completed in {workflow_duration:.2f}s"
            )

            return {
                "workflow": "full_parallel_airport_operations",
                "total_vessels": len(vessel_ids),
                "duration_seconds": workflow_duration,
                "phases": {
                    "scheduling": schedule_result,
                    "gate_assignment": assignment_result,
                    "conflict_resolution": conflict_result,
                    "resource_allocation": resource_result
                },
                "success": True
            }

        except Exception as e:
            logger.error(f"Error in full workflow: {str(e)}")
            return {
                "workflow": "full_parallel_airport_operations",
                "success": False,
                "error": str(e),
                "duration_seconds": time.time() - workflow_start
            }

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        total_executions = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.success)
        failed = total_executions - successful

        if total_executions > 0:
            avg_execution_time = sum(
                r.execution_time for r in self.execution_history
            ) / total_executions
            success_rate = (successful / total_executions) * 100
        else:
            avg_execution_time = 0
            success_rate = 0

        return {
            "total_executions": total_executions,
            "successful": successful,
            "failed": failed,
            "success_rate_percent": success_rate,
            "avg_execution_time_seconds": avg_execution_time,
            "registered_skills": len(self.skills),
            "max_parallel": self.max_parallel
        }
