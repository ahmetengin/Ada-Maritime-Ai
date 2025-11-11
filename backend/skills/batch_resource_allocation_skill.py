"""Batch Resource Allocation Skill - Airport-Style Parallel Operations"""

import asyncio
from typing import Dict, Any, List, Tuple
from datetime import datetime
from backend.skills.base_skill import BaseSkill, SkillMetadata
from backend.logger import get_logger

logger = get_logger(__name__)


class BatchResourceAllocationSkill(BaseSkill):
    """
    Allocate multiple resources (fuel, water, repairs, supplies) to multiple
    vessels in parallel with conflict detection and resolution.
    """

    def __init__(self, db_interface=None):
        super().__init__()
        self.db = db_interface
        self.resource_lock = asyncio.Lock()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="batch_resource_allocation",
            description="Allocate resources to multiple vessels in parallel",
            version="1.0.0",
            author="Ada Maritime AI",
            requires_database=True
        )

    async def execute(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Execute batch resource allocation

        Args:
            params: {
                "allocations": [
                    {"vessel_id": "V1", "resources": ["fuel", "water", "cleaning"]},
                    {"vessel_id": "V2", "resources": ["fuel", "maintenance"]},
                    ...
                ]
            }
        """
        self.validate_params(params, ["allocations"])

        allocations = params.get("allocations", [])

        logger.info(f"Starting batch resource allocation for {len(allocations)} vessels")

        try:
            # Phase 1: Flatten all resource requests
            all_requests = self._flatten_requests(allocations)

            # Phase 2: Check resource availability in parallel
            availabilities = await self._check_availability_parallel(all_requests)

            # Phase 3: Detect and resolve conflicts
            resolved = await self._resolve_resource_conflicts(
                all_requests, availabilities
            )

            # Phase 4: Allocate resources in parallel
            allocation_results = await self._allocate_resources_parallel(resolved)

            # Phase 5: Add to service queues
            queue_results = await self._add_to_service_queues(resolved)

            successful = sum(1 for r in allocation_results if r.get("success", False))
            failed = len(allocation_results) - successful

            logger.info(
                f"Resource allocation completed: {successful} successful, {failed} failed"
            )

            return {
                "operation": "batch_resource_allocation",
                "total_requests": len(all_requests),
                "allocated": successful,
                "failed": failed,
                "allocations": allocation_results,
                "queue_assignments": queue_results,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error in batch resource allocation: {str(e)}")
            return {
                "operation": "batch_resource_allocation",
                "success": False,
                "error": str(e)
            }

    def _flatten_requests(
        self,
        allocations: List[Dict[str, Any]]
    ) -> List[Tuple[str, str]]:
        """Flatten allocation requests to (vessel_id, resource_type) tuples"""
        requests = []

        for allocation in allocations:
            vessel_id = allocation.get("vessel_id")
            resources = allocation.get("resources", [])

            for resource in resources:
                requests.append((vessel_id, resource))

        logger.info(f"Flattened to {len(requests)} individual resource requests")
        return requests

    async def _check_availability_parallel(
        self,
        requests: List[Tuple[str, str]]
    ) -> List[Dict[str, Any]]:
        """Check resource availability for all requests in parallel"""
        if not self.db:
            # Mock availability
            return [
                {
                    "vessel_id": vessel_id,
                    "resource_type": resource,
                    "available": True,
                    "capacity": 100,
                    "current_usage": 30
                }
                for vessel_id, resource in requests
            ]

        tasks = [
            self.db.get_resource_availability(resource_type, vessel_id)
            for vessel_id, resource_type in requests
        ]

        availabilities = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert to dicts
        results = []
        for (vessel_id, resource), availability in zip(requests, availabilities):
            if isinstance(availability, Exception):
                results.append({
                    "vessel_id": vessel_id,
                    "resource_type": resource,
                    "available": False,
                    "error": str(availability)
                })
            else:
                results.append({
                    "vessel_id": vessel_id,
                    "resource_type": resource,
                    "available": availability.get("available", False),
                    "capacity": availability.get("capacity", 0),
                    "current_usage": availability.get("current_usage", 0)
                })

        return results

    async def _resolve_resource_conflicts(
        self,
        requests: List[Tuple[str, str]],
        availabilities: List[Dict[str, Any]]
    ) -> List[Tuple[str, str, int]]:
        """
        Detect and resolve resource conflicts
        Returns: [(vessel_id, resource_type, quantity), ...]
        """
        resolved = []

        # Group requests by resource type
        resource_groups = {}
        for (vessel_id, resource), availability in zip(requests, availabilities):
            if not availability.get("available", False):
                logger.warning(
                    f"Resource {resource} not available for vessel {vessel_id}"
                )
                continue

            if resource not in resource_groups:
                resource_groups[resource] = []

            resource_groups[resource].append({
                "vessel_id": vessel_id,
                "availability": availability
            })

        # Allocate within capacity
        for resource_type, group in resource_groups.items():
            total_capacity = group[0]["availability"].get("capacity", 100)
            current_usage = group[0]["availability"].get("current_usage", 0)
            available_capacity = total_capacity - current_usage

            # Simple equal distribution
            per_vessel = available_capacity // len(group)

            for item in group:
                quantity = min(per_vessel, 100)  # Cap at 100 units
                resolved.append((
                    item["vessel_id"],
                    resource_type,
                    quantity
                ))

        logger.info(f"Resolved {len(resolved)} resource allocations")
        return resolved

    async def _allocate_resources_parallel(
        self,
        resolved: List[Tuple[str, str, int]]
    ) -> List[Dict[str, Any]]:
        """Allocate resources in parallel"""
        if not self.db:
            # Mock allocation
            return [
                {
                    "vessel_id": vessel_id,
                    "resource_type": resource_type,
                    "quantity": quantity,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
                for vessel_id, resource_type, quantity in resolved
            ]

        async with self.resource_lock:
            tasks = [
                self.db.allocate_resource(vessel_id, resource_type, quantity)
                for vessel_id, resource_type, quantity in resolved
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert to dicts
        allocation_results = []
        for (vessel_id, resource_type, quantity), result in zip(resolved, results):
            if isinstance(result, Exception):
                allocation_results.append({
                    "vessel_id": vessel_id,
                    "resource_type": resource_type,
                    "quantity": quantity,
                    "success": False,
                    "error": str(result)
                })
            else:
                allocation_results.append({
                    "vessel_id": vessel_id,
                    "resource_type": resource_type,
                    "quantity": quantity,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                })

        return allocation_results

    async def _add_to_service_queues(
        self,
        resolved: List[Tuple[str, str, int]]
    ) -> List[Dict[str, Any]]:
        """Add vessels to service queues for each resource type"""
        queue_results = []

        # Group by vessel
        vessel_services = {}
        for vessel_id, resource_type, quantity in resolved:
            if vessel_id not in vessel_services:
                vessel_services[vessel_id] = []
            vessel_services[vessel_id].append(resource_type)

        # Add to queues (in production, would use real queue system)
        for vessel_id, services in vessel_services.items():
            queue_results.append({
                "vessel_id": vessel_id,
                "services": services,
                "queue_position": len(queue_results) + 1,
                "estimated_wait_minutes": (len(queue_results) + 1) * 15
            })

        logger.info(f"Added {len(queue_results)} vessels to service queues")
        return queue_results
