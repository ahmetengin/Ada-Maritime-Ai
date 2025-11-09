"""Berth Management Skill"""

from typing import Dict, Any
from datetime import datetime
from dataclasses import asdict

try:
    from .base_skill import BaseSkill, SkillMetadata
    from ..database import get_database
except ImportError:
    from base_skill import BaseSkill, SkillMetadata
    from database import get_database


class BerthManagementSkill(BaseSkill):
    """Berth Management Skill for Marina Operations"""

    def __init__(self):
        super().__init__()
        self.db = get_database()

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="berth_management",
            description="Search and manage marina berth availability and bookings",
            version="1.0.0",
            author="Ada Ecosystem",
            requires_database=True
        )

    async def execute(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        operation = params.get("operation")

        if operation == "search_berths":
            return await self._search_berths(params, context)
        elif operation == "create_booking":
            return await self._create_booking(params, context)
        elif operation == "list_marinas":
            return await self._list_marinas(params, context)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    async def _search_berths(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        marina_id = params.get("marina_id")
        boat_length = params.get("boat_length_meters")
        check_in = params.get("check_in")
        check_out = params.get("check_out")

        min_length = boat_length + 1.0 if boat_length else None
        max_length = boat_length + 5.0 if boat_length else None

        berths = self.db.search_available_berths(
            marina_id=marina_id,
            min_length=min_length,
            max_length=max_length,
            check_in=check_in,
            check_out=check_out
        )

        if check_in and check_out:
            check_in_dt = datetime.fromisoformat(check_in)
            check_out_dt = datetime.fromisoformat(check_out)
            nights = (check_out_dt - check_in_dt).days
        else:
            nights = 1

        results = []
        for berth in berths[:10]:
            marina = self.db.get_marina_by_id(berth.marina_id)
            results.append({
                "berth_id": berth.berth_id,
                "berth_number": berth.number,
                "marina_name": marina.name if marina else "Unknown",
                "length_meters": berth.length_meters,
                "daily_rate_eur": berth.daily_rate_eur,
                "total_price_eur": round(berth.daily_rate_eur * nights, 2),
                "nights": nights,
                "amenities": {
                    "electricity": berth.has_electricity,
                    "water": berth.has_water,
                    "wifi": berth.has_wifi
                }
            })

        return {
            "operation": "search_berths",
            "found": len(results),
            "berths": results
        }

    async def _create_booking(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        required = ["berth_id", "customer_name", "customer_email", "customer_phone",
                   "boat_name", "boat_length", "check_in", "check_out"]
        self.validate_params(params, required)

        try:
            booking = self.db.create_booking(
                berth_id=params["berth_id"],
                customer_name=params["customer_name"],
                customer_email=params["customer_email"],
                customer_phone=params["customer_phone"],
                boat_name=params["boat_name"],
                boat_length=params["boat_length"],
                check_in=params["check_in"],
                check_out=params["check_out"],
                services=params.get("services", [])
            )

            return {
                "operation": "create_booking",
                "success": True,
                "booking": asdict(booking),
                "message": f"Booking {booking.booking_id} created successfully"
            }

        except ValueError as e:
            return {
                "operation": "create_booking",
                "success": False,
                "error": str(e)
            }

    async def _list_marinas(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        marinas = self.db.get_all_marinas()
        return {
            "operation": "list_marinas",
            "count": len(marinas),
            "marinas": [asdict(m) for m in marinas]
        }
