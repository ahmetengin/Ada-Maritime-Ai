"""Maintenance management skill for marina operations"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import random

from .base_skill import BaseSkill, SkillMetadata
from ..database.models import MaintenanceRecord, MaintenanceStatus
from ..database.interface import DatabaseInterface
from ..logger import setup_logger


logger = setup_logger(__name__)


class MaintenanceSkill(BaseSkill):
    """Skill for managing marina maintenance operations"""

    def __init__(self, database: DatabaseInterface):
        self.database = database
        self.maintenance_records: List[MaintenanceRecord] = []
        super().__init__()

    def get_metadata(self) -> SkillMetadata:
        """Return skill metadata"""
        return SkillMetadata(
            name="maintenance",
            description="Manage maintenance schedules and records for marinas",
            version="1.0.0",
            author="Ada Maritime AI",
            requires_database=True
        )

    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute maintenance operations

        Operations:
            - schedule_maintenance: Schedule new maintenance task
            - get_maintenance: Get maintenance records
            - update_maintenance: Update maintenance status
            - get_upcoming: Get upcoming maintenance tasks
            - complete_maintenance: Mark maintenance as completed

        Args:
            operation: The maintenance operation to perform
            parameters: Operation-specific parameters

        Returns:
            Operation results
        """
        logger.info(f"Executing maintenance operation: {operation}")

        if operation == "schedule_maintenance":
            return await self._schedule_maintenance(parameters)
        elif operation == "get_maintenance":
            return await self._get_maintenance(parameters)
        elif operation == "update_maintenance":
            return await self._update_maintenance(parameters)
        elif operation == "get_upcoming":
            return await self._get_upcoming_maintenance(parameters)
        elif operation == "complete_maintenance":
            return await self._complete_maintenance(parameters)
        elif operation == "get_maintenance_costs":
            return await self._get_maintenance_costs(parameters)
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}"
            }

    async def _schedule_maintenance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a new maintenance task"""
        marina_id = params.get("marina_id")
        berth_id = params.get("berth_id")  # Optional, for berth-specific maintenance
        description = params.get("description")
        scheduled_date = params.get("scheduled_date")
        estimated_cost = params.get("estimated_cost", 0.0)
        currency = params.get("currency", "EUR")
        assigned_to = params.get("assigned_to")

        if not marina_id or not description or not scheduled_date:
            return {
                "success": False,
                "error": "marina_id, description, and scheduled_date required"
            }

        marina = self.database.get_marina_by_id(marina_id)
        if not marina:
            return {"success": False, "error": f"Marina {marina_id} not found"}

        # Generate maintenance ID
        maintenance_id = f"MNT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create maintenance record
        maintenance = MaintenanceRecord(
            maintenance_id=maintenance_id,
            berth_id=berth_id,
            marina_id=marina_id,
            description=description,
            scheduled_date=scheduled_date,
            completed_date=None,
            status=MaintenanceStatus.SCHEDULED.value,
            cost=estimated_cost,
            currency=currency,
            assigned_to=assigned_to
        )

        self.maintenance_records.append(maintenance)

        # If berth-specific, mark berth as maintenance
        if berth_id:
            berth = self.database.get_berth_by_id(berth_id)
            if berth:
                berth.status = "maintenance"
                berth.last_maintenance_date = scheduled_date

        logger.info(
            f"Maintenance scheduled: {maintenance_id} for marina {marina_id} "
            f"on {scheduled_date}"
        )

        return {
            "success": True,
            "maintenance_id": maintenance_id,
            "marina_id": marina_id,
            "berth_id": berth_id,
            "description": description,
            "scheduled_date": scheduled_date,
            "status": "scheduled",
            "message": "Maintenance task scheduled successfully"
        }

    async def _get_maintenance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get maintenance records"""
        marina_id = params.get("marina_id")
        berth_id = params.get("berth_id")
        status = params.get("status")

        if not marina_id:
            return {"success": False, "error": "marina_id required"}

        # Filter records
        records = [r for r in self.maintenance_records if r.marina_id == marina_id]

        if berth_id:
            records = [r for r in records if r.berth_id == berth_id]

        if status:
            records = [r for r in records if r.status == status]

        # Sort by scheduled date
        records.sort(key=lambda r: r.scheduled_date, reverse=True)

        return {
            "success": True,
            "marina_id": marina_id,
            "total_records": len(records),
            "maintenance_records": [
                {
                    "maintenance_id": r.maintenance_id,
                    "berth_id": r.berth_id,
                    "description": r.description,
                    "scheduled_date": r.scheduled_date,
                    "completed_date": r.completed_date,
                    "status": r.status,
                    "cost": r.cost,
                    "currency": r.currency,
                    "assigned_to": r.assigned_to
                }
                for r in records
            ]
        }

    async def _update_maintenance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update maintenance record status"""
        maintenance_id = params.get("maintenance_id")
        new_status = params.get("status")
        actual_cost = params.get("cost")

        if not maintenance_id or not new_status:
            return {
                "success": False,
                "error": "maintenance_id and status required"
            }

        # Find maintenance record
        maintenance = next(
            (m for m in self.maintenance_records if m.maintenance_id == maintenance_id),
            None
        )

        if not maintenance:
            return {
                "success": False,
                "error": f"Maintenance {maintenance_id} not found"
            }

        # Update status
        old_status = maintenance.status
        maintenance.status = new_status

        if actual_cost is not None:
            maintenance.cost = actual_cost

        if new_status == MaintenanceStatus.IN_PROGRESS.value:
            logger.info(f"Maintenance {maintenance_id} started")
        elif new_status == MaintenanceStatus.COMPLETED.value:
            maintenance.completed_date = datetime.now().isoformat()
            logger.info(f"Maintenance {maintenance_id} completed")

            # If berth maintenance, mark berth as available
            if maintenance.berth_id:
                berth = self.database.get_berth_by_id(maintenance.berth_id)
                if berth and berth.status == "maintenance":
                    berth.status = "available"

        return {
            "success": True,
            "maintenance_id": maintenance_id,
            "old_status": old_status,
            "new_status": new_status,
            "message": f"Maintenance status updated to {new_status}"
        }

    async def _get_upcoming_maintenance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get upcoming maintenance tasks"""
        marina_id = params.get("marina_id")
        days_ahead = params.get("days_ahead", 30)

        if not marina_id:
            return {"success": False, "error": "marina_id required"}

        # Get scheduled maintenance within the next N days
        today = datetime.now().date()
        future_date = today + timedelta(days=days_ahead)

        upcoming = []
        for record in self.maintenance_records:
            if record.marina_id == marina_id and record.status == MaintenanceStatus.SCHEDULED.value:
                scheduled_date = datetime.fromisoformat(record.scheduled_date).date()
                if today <= scheduled_date <= future_date:
                    days_until = (scheduled_date - today).days
                    upcoming.append({
                        "maintenance_id": record.maintenance_id,
                        "berth_id": record.berth_id,
                        "description": record.description,
                        "scheduled_date": record.scheduled_date,
                        "days_until": days_until,
                        "cost": record.cost,
                        "currency": record.currency,
                        "assigned_to": record.assigned_to,
                        "urgency": "high" if days_until <= 7 else "medium" if days_until <= 14 else "low"
                    })

        # Sort by date
        upcoming.sort(key=lambda x: x["days_until"])

        return {
            "success": True,
            "marina_id": marina_id,
            "days_ahead": days_ahead,
            "total_upcoming": len(upcoming),
            "upcoming_maintenance": upcoming
        }

    async def _complete_maintenance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a maintenance task"""
        maintenance_id = params.get("maintenance_id")
        actual_cost = params.get("actual_cost")
        notes = params.get("notes", "")

        if not maintenance_id:
            return {"success": False, "error": "maintenance_id required"}

        # Update to completed status
        result = await self._update_maintenance({
            "maintenance_id": maintenance_id,
            "status": MaintenanceStatus.COMPLETED.value,
            "cost": actual_cost
        })

        if result["success"]:
            result["completion_notes"] = notes
            result["completed_at"] = datetime.now().isoformat()

        return result

    async def _get_maintenance_costs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get maintenance cost summary for a marina"""
        marina_id = params.get("marina_id")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        if not marina_id:
            return {"success": False, "error": "marina_id required"}

        # Filter records
        records = [r for r in self.maintenance_records if r.marina_id == marina_id]

        if start_date:
            start_dt = datetime.fromisoformat(start_date).date()
            records = [
                r for r in records
                if datetime.fromisoformat(r.scheduled_date).date() >= start_dt
            ]

        if end_date:
            end_dt = datetime.fromisoformat(end_date).date()
            records = [
                r for r in records
                if datetime.fromisoformat(r.scheduled_date).date() <= end_dt
            ]

        # Calculate costs by status
        total_scheduled = sum(r.cost for r in records if r.status == "scheduled")
        total_completed = sum(r.cost for r in records if r.status == "completed")
        total_in_progress = sum(r.cost for r in records if r.status == "in_progress")

        # Get currency (assuming all records use same currency for this marina)
        currency = records[0].currency if records else "EUR"

        return {
            "success": True,
            "marina_id": marina_id,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "costs": {
                "scheduled": round(total_scheduled, 2),
                "in_progress": round(total_in_progress, 2),
                "completed": round(total_completed, 2),
                "total": round(total_scheduled + total_completed + total_in_progress, 2),
                "currency": currency
            },
            "record_counts": {
                "scheduled": len([r for r in records if r.status == "scheduled"]),
                "in_progress": len([r for r in records if r.status == "in_progress"]),
                "completed": len([r for r in records if r.status == "completed"]),
                "total": len(records)
            }
        }
